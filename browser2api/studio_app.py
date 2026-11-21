import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import re
from pathlib import Path
import zipfile
import io
from fastapi.responses import StreamingResponse

app = FastAPI(title="FlowGen MultiWorker Studio")

OUTPUT_DIR = Path("E:/Organized/flowgen/browser2api/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

job_state = {
    "status": "idle", # idle, running, paused, stopped
    "total": 0,
    "completed": 0,
    "failed": 0,
    "active_workers": 2,
    "logs": [],
    "items": []
}

class GenerateRequest(BaseModel):
    prompts: str
    workers: int = 2
    headless: bool = True
    style_suffix: Optional[str] = ""
    aspect_ratio: str = "1:1"
    custom_prefix: Optional[str] = "flow"

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlowGen Studio — Multi-Worker Google Flow HUD</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        obsidian: '#09090b',
                        surface: '#18181b',
                        card: '#27272a',
                    }
                }
            }
        }
    </script>
    <style>
        .mesh-gradient {
            background-image: radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                              radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
        }
        .grid-bg {
            background-size: 32px 32px;
            background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                              linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        }
    </style>
</head>
<body class="bg-slate-50 dark:bg-obsidian text-slate-900 dark:text-slate-100 min-h-screen mesh-gradient grid-bg font-sans antialiased transition-colors duration-300">
    
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-surface/70 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="w-3 h-3 rounded-full bg-indigo-500 animate-pulse"></div>
            <h1 class="font-bold text-lg tracking-tight">FlowGen <span class="text-indigo-500 font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">MULTI-WORKER HUD</span></h1>
        </div>
        <div class="flex items-center space-x-4">
            <button onclick="toggleTheme()" class="p-2 rounded-lg bg-slate-200 dark:bg-card hover:bg-slate-300 dark:hover:bg-slate-700 transition">
                <svg id="theme-icon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            </button>
            <button onclick="triggerLogin()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 transition">Google Login / Session</button>
            <button onclick="downloadZip()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition">Download ZIP Archive</button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <section class="lg:col-span-7 space-y-6">
            <div class="grid grid-cols-3 gap-4">
                <div class="p-4 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm">
                    <p class="text-xs text-slate-500 font-medium">Total Generated</p>
                    <p id="stat-total" class="text-2xl font-bold mt-1">0</p>
                </div>
                <div class="p-4 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm">
                    <p class="text-xs text-slate-500 font-medium">Active Workers</p>
                    <p id="stat-workers" class="text-2xl font-bold mt-1 text-indigo-500">2</p>
                </div>
                <div class="p-4 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm">
                    <p class="text-xs text-slate-500 font-medium">Queue Status</p>
                    <p id="stat-status" class="text-2xl font-bold mt-1 text-emerald-500">Idle</p>
                </div>
            </div>

            <div class="p-5 rounded-2xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <div class="flex items-center justify-between">
                    <label class="text-sm font-semibold">Prompt Batch (Separated by empty lines)</label>
                    <input type="text" id="custom-prefix" placeholder="File Prefix (default: flow)" class="px-3 py-1 text-xs rounded-lg bg-slate-100 dark:bg-card border border-slate-300 dark:border-slate-700">
                </div>
                <textarea id="prompt-input" rows="5" class="w-full p-4 rounded-xl bg-slate-100 dark:bg-card border border-slate-300 dark:border-slate-700 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" placeholder="Prompt 1...&#10;&#10;Prompt 2..."></textarea>

                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Preset Style Modifier</label>
                    <div class="grid grid-cols-4 gap-3">
                        <button onclick="setStyle('')" class="p-2 rounded-xl border border-indigo-500 bg-indigo-500/10 text-xs font-medium text-center transition">None</button>
                        <button onclick="setStyle(', cinematic raw, photorealistic, 8k')" class="p-2 rounded-xl border border-slate-700 hover:border-indigo-500 text-xs font-medium text-center transition bg-card/50">Cinematic</button>
                        <button onclick="setStyle(', cyberpunk neon aesthetic, glowing light, futuristic')" class="p-2 rounded-xl border border-slate-700 hover:border-indigo-500 text-xs font-medium text-center transition bg-card/50">Cyberpunk</button>
                        <button onclick="setStyle(', oil painting masterpiece, detailed brushstrokes')" class="p-2 rounded-xl border border-slate-700 hover:border-indigo-500 text-xs font-medium text-center transition bg-card/50">Oil Painting</button>
                    </div>
                </div>

                <div class="flex items-center justify-between pt-2">
                    <div class="flex items-center space-x-4">
                        <div>
                            <label class="text-xs text-slate-500 block mb-1">Workers (1-4)</label>
                            <input type="number" id="worker-count" min="1" max="4" value="2" class="w-16 p-2 rounded-lg bg-slate-100 dark:bg-card border border-slate-300 dark:border-slate-700 text-center text-sm font-bold">
                        </div>
                        <div class="flex items-center space-x-2 pt-5">
                            <input type="checkbox" id="headless-toggle" checked class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500">
                            <label for="headless-toggle" class="text-xs font-medium">Headless Browser</label>
                        </div>
                    </div>
                    
                    <div class="flex space-x-2 pt-5">
                        <button onclick="startBatch()" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition">Start</button>
                        <button onclick="controlJob('pause')" class="px-3 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-sm transition">Pause</button>
                        <button onclick="controlJob('resume')" class="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition">Resume</button>
                        <button onclick="controlJob('stop')" class="px-3 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm transition">Stop</button>
                    </div>
                </div>
            </div>
        </section>

        <section class="lg:col-span-5 space-y-6">
            <div class="p-5 rounded-2xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <div class="flex justify-between text-xs font-semibold">
                    <span id="progress-label">Progress: 0 / 0</span>
                    <span id="eta-label" class="text-indigo-400">ETA: --</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-card h-2.5 rounded-full overflow-hidden">
                    <div id="progress-bar" class="bg-indigo-500 h-full w-0 transition-all duration-300"></div>
                </div>
            </div>

            <div class="p-5 rounded-2xl bg-white dark:bg-surface border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Live Worker Stream</h3>
                <div id="console-logs" class="h-64 overflow-y-auto p-3 rounded-xl bg-slate-950 text-emerald-400 font-mono text-xs space-y-1">
                    [System] Ready for multi-worker batch execution...
                </div>
            </div>
        </section>
    </main>

    <script>
        let selectedStyle = "";
        function setStyle(style) { selectedStyle = style; alert("Style set"); }
        function toggleTheme() { document.documentElement.classList.toggle('dark'); }

        async function startBatch() {
            const prompts = document.getElementById('prompt-input').value;
            const workers = parseInt(document.getElementById('worker-count').value);
            const headless = document.getElementById('headless-toggle').checked;
            const custom_prefix = document.getElementById('custom-prefix').value || "flow";

            const res = await fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompts, workers, headless, style_suffix: selectedStyle, custom_prefix })
            });
            const data = await res.json();
            alert(data.message);
            pollStatus();
        }

        async function controlJob(action) {
            await fetch(`/api/control/${action}`, {method: 'POST'});
        }

        async function triggerLogin() {
            const res = await fetch('/api/login', {method: 'POST'});
            const data = await res.json();
            alert(data.message);
        }

        function downloadZip() {
            window.location.href = '/api/download-zip';
        }

        async function pollStatus() {
            setInterval(async () => {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('stat-total').innerText = data.completed;
                document.getElementById('stat-status').innerText = data.status;
                const pct = data.total > 0 ? (data.completed / data.total) * 100 : 0;
                document.getElementById('progress-bar').style.width = pct + '%';
                document.getElementById('progress-label').innerText = `Progress: ${data.completed} / ${data.total}`;
                if(data.logs.length > 0) {
                    document.getElementById('console-logs').innerHTML = data.logs.map(l => `<div>> ${l}</div>`).join('');
                }
            }, 1500);
        }
    </script>
</body>
</html>
"""

@app.post("/api/start")
async def start_batch(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_state["status"] = "running"
    job_state["completed"] = 0
    prompts = [p.strip() for p in re.split(r'\n\s*\n', req.prompts) if p.strip()]
    job_state["total"] = len(prompts)
    
    async def run_batch_task():
        queue = asyncio.Queue()
        for idx, p in enumerate(prompts, start=1):
            final_prompt = p + (req.style_suffix or "")
            await queue.put((idx, final_prompt))

        async def worker(wid: int):
            while not queue.empty():
                while job_state["status"] == "paused":
                    await asyncio.sleep(1)
                if job_state["status"] == "stopped":
                    break
                
                try:
                    idx, prompt = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                
                job_state["logs"].append(f"[Worker {wid}] Prompt {idx}: {prompt[:25]}...")
                
                # Auto-retry logic (up to 2 retries on simulated failure)
                success = False
                for attempt in range(3):
                    try:
                        await asyncio.sleep(1.5) # simulate generation
                        success = True
                        break
                    except Exception as e:
                        job_state["logs"].append(f"[Worker {wid}] Retry {attempt+1} for prompt {idx}")
                
                if success:
                    job_state["completed"] += 1
                    job_state["logs"].append(f"[Worker {wid}] Completed prompt {idx}")
                else:
                    job_state["failed"] += 1
                    job_state["logs"].append(f"[Worker {wid}] Failed prompt {idx}")
                queue.task_done()

        workers = [asyncio.create_task(worker(i)) for i in range(req.workers)]
        await queue.join()
        if job_state["status"] != "stopped":
            job_state["status"] = "idle"

    background_tasks.add_task(run_batch_task)
    return {"message": f"Started {len(prompts)} prompts with {req.workers} workers."}

@app.post("/api/control/{action}")
async def control(action: str):
    if action in ["pause", "stop", "resume"]:
        job_state["status"] = "resume" if action == "resume" else action
        job_state["logs"].append(f"[System] State: {action}")
        return {"status": action}
    raise HTTPException(status_code=400, detail="Invalid action")

@app.post("/api/login")
async def login_session():
    job_state["logs"].append("[System] Google Login session requested. Complete login in browser window.")
    return {"message": "Headless browser session login triggered."}

@app.get("/api/download-zip")
async def download_zip():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                zf.write(filepath, arcname=file)
    memory_file.seek(0)
    return StreamingResponse(memory_file, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=flowgen_outputs.zip"})

@app.get("/api/status")
async def get_status():
    return JSONResponse(job_state)
