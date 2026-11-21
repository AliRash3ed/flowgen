import asyncio
from pathlib import Path
import re

async def multiworker_generate(prompts_text: str, headless: bool = True, workers_count: int = 2):
    # Parse prompts separated by empty lines
    prompts = [p.strip() for p in re.split(r'\n\s*\n', prompts_text) if p.strip()]
    queue = asyncio.Queue()
    for idx, prompt in enumerate(prompts, start=1):
        await queue.put((idx, prompt))

    output_dir = Path("E:/Organized/flowgen/browser2api/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    async def worker(worker_id: int):
        while not queue.empty():
            try:
                idx, prompt = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            
            # Initial words slug for filename
            clean_slug = re.sub(r'[^a-zA-Z0-9]+', '_', prompt)[:30].strip('_')
            filename = f"{idx}.{clean_slug}.png"
            
            print(f"[Worker {worker_id}] Task {idx}: {prompt[:25]}... -> {filename} (headless={headless})")
            
            # Placeholder for actual playwright flow generation
            await asyncio.sleep(1)
            
            results.append((idx, filename))
            queue.task_done()

    workers = [asyncio.create_task(worker(i)) for i in range(workers_count)]
    await queue.join()
    for w in workers:
        w.cancel()
    
    return sorted(results)

if __name__ == "__main__":
    sample_input = "A cyberpunk hacker\n\nA futuristic Tesla car\n\nA cozy mountain cabin"
    print("Running multiworker queue:", asyncio.run(multiworker_generate(sample_input)))
