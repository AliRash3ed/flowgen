"""Multi-worker queue orchestrator for Google Flow batch generation."""

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine

from ...browser import BrowserManager
from ...types import GenerationStatus, Platform
from .client import FlowClient
from .enums import FlowCount, FlowModel, FlowOrientation
from .naming import generate_prompt_filename

logger = logging.getLogger(__name__)


@dataclass
class PromptItem:
    """Represents a single prompt task in the queue."""
    id: int
    raw_prompt: str
    effective_prompt: str
    filename_prefix: str
    target_filename: str
    status: str = "pending"  # pending, processing, completed, failed, paused
    worker_id: int | None = None
    attempts: int = 0
    max_retries: int = 2
    error: str | None = None
    duration_ms: int = 0
    images: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None


@dataclass
class WorkerState:
    """Live state of a generation worker."""
    worker_id: int
    status: str = "idle"  # idle, preparing, generating, downloading, recycling
    current_prompt_id: int | None = None
    current_prompt_text: str | None = None
    tasks_completed: int = 0
    last_active: float = field(default_factory=time.time)


class FlowOrchestrator:
    """Manages multi-worker concurrent image generation on Google Flow."""

    def __init__(
        self,
        output_dir: Path | None = None,
        max_workers: int = 2,
        headless: bool = True,
        model: FlowModel = FlowModel.NANO_BANANA_2_1,
        orientation: FlowOrientation = FlowOrientation.PORTRAIT,
        count: FlowCount = FlowCount.X1,
        naming_style: str = "dot_space",  # "dot_space", "dot_slug", "underscore"
        style_suffix: str = "",
        style_prefix: str = "",
    ):
        if output_dir is None:
            from ...config import DATA_DIR
            output_dir = DATA_DIR / "downloads" / "flow"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.max_workers = min(max(max_workers, 1), 4)
        self.headless = headless
        self.model = model
        self.orientation = orientation
        self.count = count
        self.naming_style = naming_style
        self.style_suffix = style_suffix.strip()
        self.style_prefix = style_prefix.strip()

        # Queue and items
        self.items: dict[int, PromptItem] = {}
        self.queue: asyncio.Queue[int] = asyncio.Queue()
        self.worker_states: dict[int, WorkerState] = {}
        self.generated_gallery: list[dict[str, Any]] = []

        # Lifecycle controls
        self.state: str = "idle"  # idle, running, paused, stopped, completed
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_requested = False
        self._batch_task: asyncio.Task | None = None
        self._worker_tasks: list[asyncio.Task] = []

        # Browser management
        self.browser_manager: BrowserManager | None = None
        self._context = None
        self._main_page = None

        # Telemetry
        self.start_time: float | None = None
        self.finish_time: float | None = None

        # Event callbacks
        self.on_log: list[Callable[[str, str], Coroutine[Any, Any, None] | None]] = []
        self.on_telemetry: list[Callable[[dict[str, Any]], Coroutine[Any, Any, None] | None]] = []
        self.on_item_update: list[Callable[[PromptItem], Coroutine[Any, Any, None] | None]] = []
        self.on_image_generated: list[Callable[[dict[str, Any]], Coroutine[Any, Any, None] | None]] = []

    def emit_log(self, message: str, level: str = "info") -> None:
        """Log message and notify listeners."""
        log_msg = f"[FlowOrchestrator] {message}"
        if level == "error":
            logger.error(log_msg)
        elif level == "warning":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        for cb in self.on_log:
            try:
                res = cb(message, level)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

    def emit_telemetry(self) -> None:
        """Calculate and dispatch current telemetry state."""
        stats = self.get_telemetry()
        for cb in self.on_telemetry:
            try:
                res = cb(stats)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

    def emit_item_update(self, item: PromptItem) -> None:
        """Notify listeners when an item status changes."""
        for cb in self.on_item_update:
            try:
                res = cb(item)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

    def emit_image(self, img_info: dict[str, Any]) -> None:
        """Notify listeners of newly generated image."""
        self.generated_gallery.insert(0, img_info)
        for cb in self.on_image_generated:
            try:
                res = cb(img_info)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

    def parse_prompts(self, raw_text: str) -> list[str]:
        """Split raw text separated by empty lines into cleaned prompt strings."""
        blocks = re.split(r'\n\s*\n', raw_text.strip())
        return [b.strip() for b in blocks if b.strip()]

    def set_prompts(self, prompt_list: list[str]) -> list[PromptItem]:
        """Populate the queue with ordered prompt items."""
        self.items.clear()
        created_items = []

        for idx, raw in enumerate(prompt_list, start=1):
            effective = raw.strip()
            if self.style_prefix:
                effective = f"{self.style_prefix}, {effective}"
            if self.style_suffix:
                effective = f"{effective}, {self.style_suffix}"

            filename = generate_prompt_filename(
                index=idx,
                prompt=raw,
                style=self.naming_style,
                extension=".png",
            )
            prefix = Path(filename).stem

            item = PromptItem(
                id=idx,
                raw_prompt=raw,
                effective_prompt=effective,
                filename_prefix=prefix,
                target_filename=filename,
            )
            self.items[idx] = item
            created_items.append(item)

        return created_items

    def get_telemetry(self) -> dict[str, Any]:
        """Calculate live statistics, speed, and ETA."""
        total = len(self.items)
        completed = sum(1 for item in self.items.values() if item.status == "completed")
        failed = sum(1 for item in self.items.values() if item.status == "failed")
        processing = sum(1 for item in self.items.values() if item.status == "processing")
        pending = sum(1 for item in self.items.values() if item.status == "pending")

        now = time.time()
        elapsed = (now - self.start_time) if self.start_time else 0.0

        # Calculate speed (images per minute)
        speed = 0.0
        if completed > 0 and elapsed > 1.0:
            speed = round((completed / elapsed) * 60, 1)

        # Calculate ETA (seconds)
        eta = 0
        remaining = pending + processing
        if speed > 0 and remaining > 0:
            eta = int((remaining / speed) * 60)
        elif remaining > 0 and self.state == "running":
            # Heuristic estimate based on ~24s per image divided across parallel workers
            eta = int((remaining * 24) / max(self.max_workers, 1))

        # Format ETA as mm:ss
        eta_min = eta // 60
        eta_sec = eta % 60
        eta_formatted = f"{eta_min:02d}:{eta_sec:02d}"

        # Progress percentage
        progress_pct = int((completed / total * 100)) if total > 0 else 0

        return {
            "state": self.state,
            "total": total,
            "completed": completed,
            "failed": failed,
            "processing": processing,
            "pending": pending,
            "elapsed_seconds": int(elapsed),
            "speed_images_per_min": speed,
            "speed_img_per_min": speed,
            "eta_seconds": eta,
            "eta_formatted": eta_formatted,
            "progress_pct": progress_pct,
            "workers": [
                {
                    "worker_id": ws.worker_id,
                    "status": ws.status,
                    "prompt_id": ws.current_prompt_id,
                    "prompt_text": ws.current_prompt_text,
                    "tasks_completed": ws.tasks_completed,
                    "active": ws.status in ["generating", "navigating", "busy", "starting"],
                }
                for ws in self.worker_states.values()
            ],
        }

    async def _worker_loop(self, worker_id: int, context: Any, initial_page: Any = None) -> None:
        """Dedicated execution loop for an individual worker tab."""
        # Stagger worker startup slightly to avoid simultaneous project creations
        if worker_id > 1:
            await asyncio.sleep((worker_id - 1) * 3.0)

        state = WorkerState(worker_id=worker_id, status="preparing")
        self.worker_states[worker_id] = state
        self.emit_log(f"Worker #{worker_id} initializing tab...", "info")

        page = None
        client = None

        try:
            if initial_page and worker_id == 1:
                page = initial_page
            else:
                page = await context.new_page()

            client = FlowClient(
                page=page,
                context=context,
                output_dir=self.output_dir,
                model=self.model,
                orientation=self.orientation,
                count=self.count,
            )

            state.status = "navigating"
            self.emit_telemetry()
            try:
                await client._ensure_generation_page()
                await client._setup_generation_config()
            except Exception as e:
                self.emit_log(f"Worker #{worker_id} setup notice: {e}", "warning")

            state.status = "idle"
            self.emit_log(f"Worker #{worker_id} ready.", "info")
            self.emit_telemetry()

            while not self._stop_requested:
                await self._pause_event.wait()
                if self._stop_requested:
                    break

                try:
                    item_id = self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    state.status = "idle"
                    state.current_prompt_id = None
                    state.current_prompt_text = None
                    self.emit_telemetry()
                    await asyncio.sleep(0.5)
                    # Check if all items are done
                    if all(i.status in ["completed", "failed"] for i in self.items.values()):
                        break
                    continue

                item = self.items.get(item_id)
                if not item or item.status in ["completed", "failed"]:
                    self.queue.task_done()
                    continue

                # Process this item
                item.status = "processing"
                item.worker_id = worker_id
                state.status = "generating"
                state.current_prompt_id = item.id
                state.current_prompt_text = item.raw_prompt[:40]
                self.emit_item_update(item)
                self.emit_telemetry()

                self.emit_log(
                    f"Worker #{worker_id} starting #{item.id}: {item.raw_prompt[:50]}...", "info"
                )

                t0 = time.monotonic()
                try:
                    result = await client.generate_images(
                        prompt=item.effective_prompt,
                        count=self.count.value,
                        timeout_seconds=50,
                        custom_filename_prefix=item.filename_prefix,
                        flat_output=True,
                    )

                    duration = int((time.monotonic() - t0) * 1000)
                    item.duration_ms = duration

                    if result.status == GenerationStatus.COMPLETED and result.images:
                        item.status = "completed"
                        item.completed_at = time.time()
                        state.tasks_completed += 1

                        for g_img in result.images:
                            img_dict = {
                                "id": f"{item.id}_{g_img.filename}",
                                "prompt_id": item.id,
                                "prompt": item.raw_prompt,
                                "effective_prompt": item.effective_prompt,
                                "filename": g_img.filename,
                                "local_path": g_img.local_path,
                                "url": g_img.url,
                                "width": g_img.width,
                                "height": g_img.height,
                                "model": self.model.value,
                                "orientation": self.orientation.value,
                                "worker_id": worker_id,
                                "duration_ms": duration,
                                "timestamp": time.time(),
                            }
                            item.images.append(img_dict)
                            self.emit_image(img_dict)

                        self.emit_log(
                            f"Worker #{worker_id} finished #{item.id} -> {item.target_filename} ({duration}ms)",
                            "info",
                        )
                    else:
                        raise RuntimeError(result.error or "Generation failed or returned 0 images")

                except Exception as exc:
                    item.attempts += 1
                    error_msg = str(exc)
                    self.emit_log(
                        f"Worker #{worker_id} error on #{item.id} (attempt {item.attempts}): {error_msg}",
                        "warning",
                    )

                    if item.attempts < item.max_retries and not self._stop_requested:
                        # Put back to queue for auto-retry
                        self.emit_log(f"Auto-retrying prompt #{item.id} (up to {item.max_retries}x)...", "info")
                        item.status = "pending"
                        await asyncio.sleep(2)
                        await self.queue.put(item.id)
                    else:
                        item.status = "failed"
                        item.error = error_msg
                        self.emit_log(f"Prompt #{item.id} permanently failed after {item.attempts} attempts.", "error")

                finally:
                    self.queue.task_done()
                    self.emit_item_update(item)
                    self.emit_telemetry()

                # Memory leak prevention: refresh tab after 15 generations
                if state.tasks_completed > 0 and state.tasks_completed % 15 == 0:
                    self.emit_log(
                        f"Worker #{worker_id} completed {state.tasks_completed} tasks. Recycling tab memory...",
                        "info",
                    )
                    state.status = "recycling"
                    self.emit_telemetry()
                    try:
                        await page.reload(wait_until="domcontentloaded")
                        await asyncio.sleep(3)
                        await client._ensure_generation_page()
                    except Exception as e:
                        logger.warning(f"Worker #{worker_id} tab recycle note: {e}")

        except asyncio.CancelledError:
            self.emit_log(f"Worker #{worker_id} cancelled.", "info")
        except Exception as e:
            self.emit_log(f"Worker #{worker_id} fatal exception: {e}", "error")
        finally:
            state.status = "closed"
            self.emit_telemetry()
            if page:
                try:
                    await page.close()
                except Exception:
                    pass

    async def start(self) -> None:
        """Launch browser and dispatch multi-worker parallel execution."""
        if self.state == "running":
            self.emit_log("Batch is already running.", "warning")
            return

        if not self.items:
            self.emit_log("No prompts in queue to process.", "warning")
            return

        self.state = "running"
        self._stop_requested = False
        self._pause_event.set()
        self.start_time = time.time()
        self.finish_time = None
        # The API returns the whole process-wide gallery. Clearing it keeps a
        # batch response limited to the images this run actually generated.
        self.generated_gallery.clear()

        # Reset item states that are not completed
        for item in self.items.values():
            if item.status != "completed":
                item.status = "pending"
                item.attempts = 0
                item.error = None
                await self.queue.put(item.id)

        self.emit_log(
            f"Starting generation batch: {len(self.items)} prompts with {self.max_workers} workers (Headless={self.headless})",
            "info",
        )
        self.emit_telemetry()

        # Launch Chrome with persistent profile
        self.browser_manager = BrowserManager()
        self.emit_log(
            f"Launching Google Chrome CDP session (Headless={self.headless})...",
            "info",
        )

        try:
            self._context, self._main_page = await self.browser_manager.launch_for_generation(
                Platform.FLOW, headless=self.headless
            )
        except Exception as e:
            self.state = "failed"
            self.emit_log(f"Failed to launch Chrome session: {e}", "error")
            self.emit_telemetry()
            return

        # Start workers
        self._worker_tasks = [
            asyncio.create_task(self._worker_loop(w_id + 1, self._context, self._main_page if w_id == 0 else None))
            for w_id in range(self.max_workers)
        ]

        # Monitor completion in background
        self._batch_task = asyncio.create_task(self._monitor_batch())

    async def _monitor_batch(self) -> None:
        """Awaits worker tasks and finalizes batch status."""
        try:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        finally:
            self.finish_time = time.time()
            if self._stop_requested:
                self.state = "stopped"
                self.emit_log("Batch execution was stopped by user.", "warning")
            else:
                self.state = "completed"
                self.emit_log("Batch execution complete! All prompts processed.", "info")

            self.emit_telemetry()

    def pause(self) -> None:
        """Pause active queue dispatch."""
        if self.state == "running":
            self._pause_event.clear()
            self.state = "paused"
            self.emit_log("Batch paused. Current tasks will finish, then queue will hold.", "info")
            self.emit_telemetry()

    def resume(self) -> None:
        """Resume paused queue dispatch."""
        if self.state == "paused":
            self._pause_event.set()
            self.state = "running"
            self.emit_log("Batch resumed. Dispatching next queue items.", "info")
            self.emit_telemetry()

    async def stop(self) -> None:
        """Abort execution gracefully and close browser."""
        self._stop_requested = True
        self._pause_event.set()
        self.state = "stopped"
        self.emit_log("Stopping batch execution...", "warning")

        # Cancel worker tasks
        for task in self._worker_tasks:
            task.cancel()

        # Clear remaining queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except Exception:
                break

        if self.browser_manager:
            self.emit_log("Closing browser session...", "info")
            try:
                await self.browser_manager.close()
            except Exception:
                pass
            self.browser_manager = None

        self.emit_telemetry()

    async def retry_failed(self) -> None:
        """Re-queue failed prompts and restart if needed."""
        failed_items = [i for i in self.items.values() if i.status == "failed"]
        if not failed_items:
            self.emit_log("No failed prompts to retry.", "info")
            return

        self.emit_log(f"Re-queuing {len(failed_items)} failed prompts...", "info")
        for item in failed_items:
            item.status = "pending"
            item.attempts = 0
            item.error = None
            self.emit_item_update(item)
            await self.queue.put(item.id)

        if self.state in ["completed", "stopped", "idle"]:
            await self.start()
        else:
            self.emit_telemetry()
