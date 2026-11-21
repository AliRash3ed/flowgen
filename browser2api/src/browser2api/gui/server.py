"""FastAPI server providing FlowGen HUD REST endpoints, AI Agent API harness, and WebSockets."""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config import DATA_DIR
from ..history import tracker
from ..platforms.flow.auth import check_active_login, has_saved_session, interactive_login
from ..platforms.flow.enums import FlowCount, FlowModel, FlowOrientation
from ..platforms.flow.multiworker import FlowOrchestrator

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_OUTPUT_DIR = Path("E:/Organized/flowgen/browser2api/output")
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Index any existing images on startup
tracker.index_existing_output_dir(DEFAULT_OUTPUT_DIR)

app = FastAPI(title="FlowGen Studio API & AI Agent Harness", version="2.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: list[WebSocket] = []

# Global Orchestrator instance
orchestrator = FlowOrchestrator(
    output_dir=DEFAULT_OUTPUT_DIR,
    max_workers=2,
    headless=True,
)


class StartBatchRequest(BaseModel):
    prompts: list[str]
    workers: int = 2
    headless: bool = True
    model: str = "nano_banana_2_1"
    orientation: str = "portrait"
    count: int = 1
    naming_style: str = "dot_space"
    style_suffix: str = ""
    style_prefix: str = ""
    output_dir: str | None = None
    project_name: str | None = "Project 1"
    use_project_subfolder: bool = True
    wait_for_completion: bool = False


class OpenFolderRequest(BaseModel):
    path: str | None = None


class OpenFileRequest(BaseModel):
    filepath: str


class SwitchAccountRequest(BaseModel):
    account_id: str


class AddAccountRequest(BaseModel):
    alias: str


async def broadcast_ws(event_type: str, data: Any) -> None:
    """Send JSON message to all connected WebSocket clients."""
    payload = {"type": event_type, "data": data}
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_json(payload)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in active_connections:
            active_connections.remove(ws)


# Bind Orchestrator callbacks to WebSocket broadcast
async def _on_log(msg: str, level: str):
    await broadcast_ws("log", {"message": msg, "level": level, "timestamp": time.time()})


async def _on_telemetry(stats: dict[str, Any]):
    await broadcast_ws("telemetry", stats)


async def _on_item_update(item: Any):
    await broadcast_ws("item_update", {
        "id": item.id,
        "raw_prompt": item.raw_prompt,
        "effective_prompt": item.effective_prompt,
        "filename": item.target_filename,
        "status": item.status,
        "worker_id": item.worker_id,
        "attempts": item.attempts,
        "duration_ms": item.duration_ms,
        "error": item.error,
        "images": item.images,
    })


async def _on_image(img_info: dict[str, Any]):
    await broadcast_ws("image_generated", img_info)


orchestrator.on_log.append(_on_log)
orchestrator.on_telemetry.append(_on_telemetry)
orchestrator.on_item_update.append(_on_item_update)
orchestrator.on_image_generated.append(_on_image)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({
            "type": "init",
            "data": {
                "telemetry": orchestrator.get_telemetry(),
                "items": [
                    {
                        "id": item.id,
                        "raw_prompt": item.raw_prompt,
                        "effective_prompt": item.effective_prompt,
                        "filename": item.target_filename,
                        "status": item.status,
                        "worker_id": item.worker_id,
                        "attempts": item.attempts,
                        "duration_ms": item.duration_ms,
                        "error": item.error,
                        "images": item.images,
                    }
                    for item in orchestrator.items.values()
                ],
                "gallery": orchestrator.generated_gallery if orchestrator.generated_gallery else tracker.data.get("images", [])[:40],
                "has_session": has_saved_session(),
                "output_dir": str(orchestrator.output_dir),
            }
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


# =====================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# =====================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Returns analytics data (lifetime, today, this week, daily trends, model distribution)."""
    return tracker.get_analytics()


# =====================================================================
# AI AGENT REST API HARNESS (v1)
# =====================================================================

@app.post("/api/v1/generate")
async def api_generate_images(req: StartBatchRequest):
    """Programmatic API harness for AI agents (Claude, Cursor, Antigravity, custom scripts)."""
    clean_prompts = [p.strip() for p in req.prompts if p.strip()]
    if not clean_prompts:
        raise HTTPException(status_code=400, detail="No prompts provided.")

    if orchestrator.state == "running":
        raise HTTPException(status_code=429, detail="A generation batch is already in progress.")

    # Configure orchestrator
    model_enum = FlowModel(req.model) if req.model in [m.value for m in FlowModel] else FlowModel.NANO_BANANA_2_1
    orient_enum = FlowOrientation(req.orientation) if req.orientation in [o.value for o in FlowOrientation] else FlowOrientation.PORTRAIT

    orchestrator.max_workers = min(max(req.workers, 1), 4)
    orchestrator.headless = req.headless
    orchestrator.model = model_enum
    orchestrator.orientation = orient_enum
    orchestrator.style_suffix = req.style_suffix
    orchestrator.style_prefix = req.style_prefix
    orchestrator.naming_style = req.naming_style
    orchestrator.set_prompts(clean_prompts)

    batch_id = f"batch_{int(time.time())}"
    t0 = time.time()

    if req.wait_for_completion:
        # Synchronous execution for agent caller
        await orchestrator.start()
        while orchestrator.state == "running":
            await asyncio.sleep(0.5)

        duration = time.time() - t0
        images = orchestrator.generated_gallery

        tracker.record_batch_completed(
            batch_id=batch_id,
            prompts=clean_prompts,
            model=model_enum.value,
            orientation=orient_enum.value,
            workers=orchestrator.max_workers,
            duration_seconds=duration,
            generated_images=images,
            status="completed" if images else "failed"
        )

        return {
            "status": "completed",
            "batch_id": batch_id,
            "prompts_count": len(clean_prompts),
            "images_count": len(images),
            "duration_seconds": round(duration, 1),
            "images": images,
        }
    else:
        # Async background execution
        asyncio.create_task(orchestrator.start())
        return {
            "status": "started",
            "batch_id": batch_id,
            "prompts_count": len(clean_prompts),
            "workers": orchestrator.max_workers,
            "poll_url": f"/api/v1/tasks/{batch_id}",
        }


@app.get("/api/v1/tasks/{batch_id}")
async def api_get_task_status(batch_id: str):
    """Poll batch status for asynchronous execution."""
    is_running = orchestrator.state == "running"
    images = orchestrator.generated_gallery
    items = [
        {
            "id": item.id,
            "status": item.status,
            "error": item.error,
            "images": item.images,
        }
        for item in orchestrator.items.values()
    ]
    completed_count = sum(1 for item in orchestrator.items.values() if item.status == "completed")
    total_count = len(orchestrator.items)
    status_str = "running" if is_running else ("completed" if completed_count >= total_count and total_count > 0 else "idle")
    return {
        "batch_id": batch_id,
        "status": status_str,
        "state": orchestrator.state,
        "completed": completed_count,
        "total": total_count,
        "images": images,
        "items": items,
    }


@app.get("/api/v1/status")
async def api_engine_status():
    """Engine health check and readiness for AI agents."""
    return {
        "engine": "FlowGen Studio API & Harness",
        "version": "2.4.0",
        "status": "online",
        "state": orchestrator.state,
        "workers_online": orchestrator.max_workers,
        "auth_ready": has_saved_session(),
        "models_available": ["nano_banana_2_1", "nano_banana_pro", "nano_banana_2_lite"],
        "aspect_ratios": ["portrait", "landscape"],
        "mcp_enabled": True
    }


@app.get("/api/v1/history")
async def api_get_history():
    """Retrieve historical project data for AI agent harness."""
    return tracker.get_analytics()


# =====================================================================
# AUTH & MULTI-ACCOUNT MANAGEMENT
# =====================================================================

ACCOUNTS_FILE = DATA_DIR / "browser_data" / "accounts.json"


def _get_accounts_data() -> dict[str, Any]:
    if ACCOUNTS_FILE.exists():
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "active_account": "default",
        "accounts": [
            {
                "id": "default",
                "alias": "Default Google Account",
                "email": "Active Session",
                "has_session": has_saved_session(),
                "created_at": time.time(),
                "last_active": time.time()
            }
        ]
    }


def _save_accounts_data(data: dict[str, Any]) -> None:
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@app.get("/api/auth/status")
async def auth_status():
    has_session = has_saved_session()
    return {
        "has_session": has_session,
        "status": "ready" if has_session else "not_configured"
    }


@app.get("/api/auth/accounts")
async def list_accounts():
    """List all saved Google Flow account sessions."""
    data = _get_accounts_data()
    for acc in data.get("accounts", []):
        if acc["id"] == "default":
            acc["has_session"] = has_saved_session()
    return data


@app.post("/api/auth/switch")
async def switch_account(req: SwitchAccountRequest):
    """Switch the active Google Flow account profile."""
    data = _get_accounts_data()
    acc_ids = [a["id"] for a in data.get("accounts", [])]
    if req.account_id not in acc_ids:
        raise HTTPException(status_code=404, detail="Account not found")

    data["active_account"] = req.account_id
    _save_accounts_data(data)
    await broadcast_ws("auth_update", {
        "message": f"Switched active account to: {req.account_id}",
        "success": True,
        "has_session": has_saved_session()
    })
    return {"status": "switched", "active_account": req.account_id}


@app.post("/api/auth/add")
async def add_account(req: AddAccountRequest):
    """Trigger headed login for a new Google account alias."""
    alias = req.alias.strip() or f"Account_{int(time.time())}"
    acc_id = f"acc_{int(time.time())}"

    data = _get_accounts_data()
    data["accounts"].append({
        "id": acc_id,
        "alias": alias,
        "email": "Pending Login",
        "has_session": False,
        "created_at": time.time(),
        "last_active": time.time()
    })
    _save_accounts_data(data)

    async def run_login():
        def update_cb(msg: str):
            asyncio.create_task(broadcast_ws("auth_update", {"message": msg}))

        success = await interactive_login(on_update=update_cb)
        if success:
            d = _get_accounts_data()
            for a in d["accounts"]:
                if a["id"] == acc_id:
                    a["has_session"] = True
                    a["email"] = "Authenticated User"
            d["active_account"] = acc_id
            _save_accounts_data(d)

        await broadcast_ws("auth_update", {
            "message": f"Account '{alias}' added!" if success else "Login cancelled",
            "success": success,
            "has_session": has_saved_session()
        })

    asyncio.create_task(run_login())
    return {"status": "started", "account_id": acc_id, "alias": alias}


@app.post("/api/auth/logout")
async def auth_logout():
    """Clear cookies and local session for the active Google account."""
    profile_dir = DATA_DIR / "browser_data" / "flow_cdp"
    if profile_dir.exists():
        cookies_file = profile_dir / "Default" / "Network" / "Cookies"
        if cookies_file.exists():
            try:
                cookies_file.unlink()
            except Exception:
                pass
    await broadcast_ws("auth_update", {
        "message": "Logged out from current Google session.",
        "success": True,
        "has_session": has_saved_session()
    })
    return {"status": "logged_out"}


@app.post("/api/auth/login")
async def auth_login():
    """Trigger headed Chrome window for Google Flow login."""
    async def run_login():
        def update_cb(msg: str):
            asyncio.create_task(broadcast_ws("auth_update", {"message": msg}))

        success = await interactive_login(on_update=update_cb)
        await broadcast_ws("auth_update", {
            "message": "Login successful! Session stored." if success else "Login failed or cancelled.",
            "success": success,
            "has_session": has_saved_session(),
        })

    asyncio.create_task(run_login())
    return {"status": "started", "message": "Launching login browser..."}


# =====================================================================
# QUEUE LIFECYCLE CONTROLS
# =====================================================================

@app.post("/api/queue/start")
async def queue_start(req: StartBatchRequest):
    global orchestrator

    if orchestrator.state == "running":
        raise HTTPException(status_code=400, detail="A batch is already running. Please pause or stop it first.")

    project_name = (req.project_name or "Project 1").strip()
    base_dir = Path(req.output_dir) if req.output_dir and req.output_dir.strip() else DEFAULT_OUTPUT_DIR

    if req.use_project_subfolder and project_name:
        import re
        safe_folder = re.sub(r'[\\/*?:"<>|]', '_', project_name).strip() or "Project"
        out_dir = base_dir / safe_folder
    else:
        out_dir = base_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    model_enum = FlowModel(req.model) if req.model in [m.value for m in FlowModel] else FlowModel.NANO_BANANA_2_1
    orient_enum = FlowOrientation(req.orientation) if req.orientation in [o.value for o in FlowOrientation] else FlowOrientation.PORTRAIT
    count_enum = FlowCount(req.count) if req.count in [1, 2, 3, 4] else FlowCount.X1

    orchestrator.output_dir = out_dir
    orchestrator.max_workers = min(max(req.workers, 1), 4)
    orchestrator.headless = req.headless
    orchestrator.model = model_enum
    orchestrator.orientation = orient_enum
    orchestrator.count = count_enum
    orchestrator.naming_style = req.naming_style
    orchestrator.style_suffix = req.style_suffix
    orchestrator.style_prefix = req.style_prefix

    clean_prompts = [p.strip() for p in req.prompts if p.strip()]
    if not clean_prompts:
        raise HTTPException(status_code=400, detail="No valid prompts provided.")

    orchestrator.set_prompts(clean_prompts)

    # Launch generation in background
    batch_id = f"batch_{int(time.time())}"
    t0 = time.time()

    async def run_batch_and_record():
        await orchestrator.start()
        # Record in history tracker upon completion
        while orchestrator.state == "running":
            await asyncio.sleep(1.0)
        dur = time.time() - t0
        tracker.record_batch_completed(
            batch_id=batch_id,
            prompts=clean_prompts,
            model=model_enum.value,
            orientation=orient_enum.value,
            workers=orchestrator.max_workers,
            duration_seconds=dur,
            generated_images=orchestrator.generated_gallery,
            project_name=project_name,
            output_dir=str(out_dir.resolve()),
            status="completed" if orchestrator.generated_gallery else "failed"
        )

    asyncio.create_task(run_batch_and_record())

    return {
        "status": "started",
        "batch_id": batch_id,
        "project_name": project_name,
        "total_prompts": len(clean_prompts),
        "workers": orchestrator.max_workers,
        "headless": orchestrator.headless,
        "output_dir": str(orchestrator.output_dir),
    }


@app.post("/api/queue/pause")
async def queue_pause():
    orchestrator.pause()
    return {"status": "paused"}


@app.post("/api/queue/resume")
async def queue_resume():
    orchestrator.resume()
    return {"status": "resumed"}


@app.post("/api/queue/stop")
async def queue_stop():
    await orchestrator.stop()
    return {"status": "stopped"}


@app.post("/api/queue/restart")
async def queue_restart():
    """Stop active workers, reset all items to pending, and restart batch."""
    await orchestrator.stop()
    for item in orchestrator.items.values():
        item.status = "pending"
        item.attempts = 0
        item.error = None
    asyncio.create_task(orchestrator.start())
    return {"status": "restarted"}


@app.post("/api/queue/retry-failed")
async def queue_retry_failed():
    asyncio.create_task(orchestrator.retry_failed())
    return {"status": "retrying"}


@app.get("/api/config/paths")
async def get_config_paths():
    """Return default output directory and list of existing projects."""
    projects = []
    seen = set()
    for b in tracker.data.get("batches", []):
        pn = b.get("project_name")
        if pn and pn not in seen:
            seen.add(pn)
            projects.append(pn)

    return {
        "default_output_dir": str(DEFAULT_OUTPUT_DIR.resolve()),
        "current_output_dir": str(orchestrator.output_dir.resolve()),
        "projects": projects
    }


@app.post("/api/open-folder")
async def open_output_folder(req: OpenFolderRequest = None):
    """Open current output directory or specific project folder in Windows File Explorer."""
    raw_path = (req.path.strip() if req and req.path and req.path.strip() else str(orchestrator.output_dir))
    target_path = Path(raw_path).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer.exe", str(target_path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target_path)])
        else:
            subprocess.Popen(["xdg-open", str(target_path)])
        return {"status": "opened", "path": str(target_path)}
    except Exception as e:
        logger.error(f"Failed to open folder {target_path} via subprocess: {e}")
        if sys.platform == "win32":
            try:
                os.startfile(str(target_path))
                return {"status": "opened_fallback", "path": str(target_path)}
            except Exception as e2:
                raise HTTPException(status_code=500, detail=str(e2))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/open-file")
async def open_file_in_explorer(req: OpenFileRequest):
    """Highlight specific file in Windows File Explorer."""
    fpath = Path(req.filepath).resolve()
    if not fpath.exists():
        if fpath.parent.exists():
            if sys.platform == "win32":
                os.startfile(str(fpath.parent))
            else:
                subprocess.Popen(["xdg-open", str(fpath.parent)])
            return {"status": "opened_parent", "path": str(fpath.parent)}
        raise HTTPException(status_code=404, detail="File does not exist")

    try:
        if sys.platform == "win32":
            subprocess.Popen(f'explorer.exe /select,"{fpath}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(fpath)])
        else:
            subprocess.Popen(["xdg-open", str(fpath.parent)])
        return {"status": "highlighted", "path": str(fpath)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# AI AGENT MCP & API KEY REMOTE HOSTING ENDPOINTS
# =====================================================================
import secrets
CONFIG_KEY_FILE = DATA_DIR / "api_key.txt"

def get_or_create_api_key() -> str:
    env_key = os.environ.get("FLOWGEN_API_KEY", "").strip()
    if env_key:
        return env_key
    if CONFIG_KEY_FILE.exists():
        try:
            key = CONFIG_KEY_FILE.read_text(encoding="utf-8").strip()
            if key:
                return key
        except Exception:
            pass
    new_key = f"fg_live_{secrets.token_hex(16)}"
    try:
        CONFIG_KEY_FILE.write_text(new_key, encoding="utf-8")
    except Exception:
        pass
    return new_key


@app.get("/api/agent/key")
async def get_agent_key():
    """Return active API key, Claude Desktop configuration, and Cursor MCP config."""
    key = get_or_create_api_key()
    py_path = sys.executable
    mcp_script = str(Path(__file__).resolve().parent.parent.parent.parent / "run_mcp.py")
    return {
        "api_key": key,
        "env_var_active": bool(os.environ.get("FLOWGEN_API_KEY")),
        "mcp_stdio_config": {
            "mcpServers": {
                "flowgen": {
                    "command": py_path,
                    "args": [mcp_script],
                    "env": {
                        "FLOWGEN_API_KEY": key
                    }
                }
            }
        },
        "colab_vps_curl_example": f'curl -X POST "http://YOUR_SERVER_OR_TUNNEL/api/batch/start" -H "x-api-key: {key}" -H "Content-Type: application/json" -d \'{{"prompts": ["A cybernetic supercar in neon rain"]}}\''
    }


@app.post("/api/agent/key/generate")
async def generate_new_api_key():
    """Rotate and generate a new API key."""
    new_key = f"fg_live_{secrets.token_hex(16)}"
    try:
        CONFIG_KEY_FILE.write_text(new_key, encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"api_key": new_key, "status": "generated"}


class McpCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


@app.post("/api/mcp/call")
async def mcp_call_endpoint(req: McpCallRequest):
    """Realtime REST execution endpoint for AI Agents connecting via HTTP/MCP."""
    from ..mcp_server import handle_tool_call
    try:
        result = await handle_tool_call(req.name, req.arguments)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/media/{file_path:path}")
async def get_media_file(file_path: str):
    """Serve local generated image files to the HUD gallery."""
    p = Path(file_path)
    candidates = [
        p,
        orchestrator.output_dir / file_path,
        Path("browser2api/output") / file_path,
        Path("output") / file_path,
    ]
    for cand in candidates:
        if cand.exists() and cand.is_file():
            return FileResponse(cand, media_type="image/png")

    # Search in tracker
    for img in tracker.data.get("images", []):
        if img.get("filename") == file_path:
            lp = Path(img.get("local_path", ""))
            if lp.exists() and lp.is_file():
                return FileResponse(lp, media_type="image/png")

    # Recursive filename search in known output dirs
    for base in [orchestrator.output_dir, Path("browser2api/output"), Path("output")]:
        if base.exists():
            matched = list(base.rglob(Path(file_path).name))
            if matched and matched[0].is_file():
                return FileResponse(matched[0], media_type="image/png")

    raise HTTPException(status_code=404, detail="Image not found")


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon():
    fav_file = STATIC_DIR / "assets" / "fg_star_logo_transparent.png"
    if fav_file.exists():
        return FileResponse(fav_file, media_type="image/png")
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return {"error": "HUD frontend static files not found."}
    return FileResponse(index_file)


def start_gui_server(host: str = "127.0.0.1", port: int = 8787):
    """Launch HUD server using Uvicorn."""
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_gui_server()
