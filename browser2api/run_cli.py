"""Direct CLI multi-worker batch generation for Google Flow."""

import argparse
import asyncio
import logging
from pathlib import Path
import sys

# Ensure package root is in sys.path
package_root = Path(__file__).resolve().parent / "src"
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

from browser2api.platforms.flow.enums import (
    MODEL_NAMES,
    FlowCount,
    FlowModel,
    FlowOrientation,
)
from browser2api.platforms.flow.multiworker import FlowOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


async def main():
    parser = argparse.ArgumentParser(description="Multi-worker Google Flow batch generator CLI")
    parser.add_argument("file_or_prompts", help="Path to text file containing prompts (separated by empty lines), or inline prompt text")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel worker tabs (1-4, default: 2)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run Chrome headless (default: True)")
    parser.add_argument("--headed", dest="headless", action="store_false", help="Show Chrome window during generation")
    parser.add_argument("--model", default="nano-banana-2.1", help="Flow model name (e.g. nano-banana-2.1, imagen-4)")
    parser.add_argument("--orientation", default="portrait", choices=["portrait", "landscape"], help="Aspect ratio (portrait=9:16, landscape=16:9)")
    parser.add_argument("--count", type=int, default=1, choices=[1, 2, 3, 4], help="Images per prompt")
    parser.add_argument("--naming", default="dot_space", choices=["dot_space", "dot_slug", "underscore"], help="Naming convention (e.g. 1. prompt initial words.png)")
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parent / "output"), help="Output directory")
    parser.add_argument("--style-suffix", default="", help="Optional style text to append to all prompts")
    parser.add_argument("--style-prefix", default="", help="Optional style text to prepend to all prompts")

    args = parser.parse_args()

    # Read prompts
    p_path = Path(args.file_or_prompts)
    if p_path.exists() and p_path.is_file():
        raw_text = p_path.read_text(encoding="utf-8")
    else:
        raw_text = args.file_or_prompts

    model_enum = MODEL_NAMES.get(args.model.lower(), FlowModel.NANO_BANANA_2_1)
    orient_enum = FlowOrientation(args.orientation)
    count_enum = FlowCount(args.count)

    orchestrator = FlowOrchestrator(
        output_dir=Path(args.output_dir),
        max_workers=args.workers,
        headless=args.headless,
        model=model_enum,
        orientation=orient_enum,
        count=count_enum,
        naming_style=args.naming,
        style_suffix=args.style_suffix,
        style_prefix=args.style_prefix,
    )

    prompts = orchestrator.parse_prompts(raw_text)
    if not prompts:
        print("[Error] No valid prompts found in input.")
        sys.exit(1)

    print(f"\n[FlowGen] Loaded {len(prompts)} prompts. Initializing {args.workers} workers (Headless={args.headless})...")
    orchestrator.set_prompts(prompts)

    def print_log(msg, level):
        print(f"[{level.upper()}] {msg}")

    orchestrator.on_log.append(print_log)

    await orchestrator.start()
    if orchestrator._batch_task:
        await orchestrator._batch_task

    print("\n[FlowGen] Batch completed successfully! All images stored at:", orchestrator.output_dir)


if __name__ == "__main__":
    asyncio.run(main())
