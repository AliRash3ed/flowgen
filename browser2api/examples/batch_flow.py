import argparse
import asyncio
import logging
from pathlib import Path

from browser2api import BrowserManager, Platform
from browser2api.platforms.flow import FlowClient, FlowCount, FlowModel, FlowOrientation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "output"

async def batch_generate(
    prompts: list[str],
    output_dir: Path,
    model: FlowModel = FlowModel.NANO_BANANA_2_1,
    orientation: FlowOrientation = FlowOrientation.PORTRAIT,
    count: FlowCount = FlowCount.X1,
):
    """Keep Chrome open once, generate all prompts sequentially, then close."""
    bm = BrowserManager()
    try:
        print("Launching Chrome once for all images...")
        context, page = await bm.launch_for_login(Platform.FLOW)

        client = FlowClient(
            page,
            context,
            output_dir=output_dir,
            model=model,
            orientation=orientation,
            count=count,
        )

        results = []
        for i, prompt in enumerate(prompts, start=1):
            print(f"\n==========================================")
            print(f"[{i}/{len(prompts)}] Generating: {prompt[:60]}...")
            print(f"Model: {model.name} | Orientation: {orientation.value} | Count: {count.value}")
            print(f"==========================================")

            res = await client.generate_images(prompt, timeout_seconds=45)
            results.append(res)
            print(f"Status: {res.status.value} ({res.duration_ms}ms)")
            for img in res.images:
                print(f"  -> Saved: {img.local_path} ({img.width}x{img.height})")

        print("\nAll generations finished successfully!")
        return results

    finally:
        print("Closing Chrome browser now...")
        await bm.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch generate Flow images in single browser session")
    parser.add_argument("prompts", nargs="+", help="Prompts to generate")
    parser.add_argument("--model", default="nano-banana-2.1")
    parser.add_argument("--orientation", default="portrait", choices=["landscape", "portrait"])
    parser.add_argument("--count", type=int, default=1, choices=[1, 2, 3, 4])
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))

    args = parser.parse_args()

    from browser2api.platforms.flow.enums import MODEL_NAMES
    m = MODEL_NAMES.get(args.model, FlowModel.NANO_BANANA_2_1)
    o = FlowOrientation(args.orientation)
    c = FlowCount(args.count)

    asyncio.run(batch_generate(args.prompts, Path(args.output_dir), model=m, orientation=o, count=c))
