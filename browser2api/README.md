# FlowGen Image Studio ⚡

<p align="center">
  <img src="browser2api/src/browser2api/gui/static/assets/fg_star_logo_transparent.png" width="96" height="96" alt="FlowGen Logo">
</p>

<p align="center">
  <strong>STREAM SERIOUSLY. SOLVE OBSESSIVELY.</strong><br>
  High-Throughput Parallel Batch Image Generation on Google Flow & Realtime MCP Agent Server
</p>

<p align="center">
  <a href="https://github.com/AliRash3ed/flowgen"><img src="https://img.shields.io/badge/FlowGen-v2.5-8b5cf6?style=flat-square" alt="Version"></a>
  <a href="https://playwright.dev"><img src="https://img.shields.io/badge/Engine-Playwright%20CDP-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-2024%20Standard-06b6d4?style=flat-square" alt="MCP"></a>
  <a href="https://colab.research.google.com"><img src="https://img.shields.io/badge/Google%20Colab-1--Click%20Launch-f59e0b?style=flat-square&logo=googlecolab&logoColor=white" alt="Colab"></a>
  <a href="https://github.com/AliRash3ed"><img src="https://img.shields.io/badge/Architect-Ali%20Bhatti-ec4899?style=flat-square&logo=github&logoColor=white" alt="Author"></a>
</p>

---

## ⚡ What is FlowGen?

**FlowGen Image Studio** connects local Google Flow accounts into an **unlimited, high-speed batch image generation engine**. It bypasses rigid rate limitations through **parallel Chromium worker tabs**, guarantees zero image overwrites with **deterministic sequential filename slugs**, and provides a **native Model Context Protocol (MCP) server** so AI agents (**Claude Desktop**, **Cursor**, **Antigravity**) can generate images directly.

### ✨ Key Features
- **Parallel Multi-Worker Tabs**: Generate 2x to 4x faster with concurrent browser tab execution.
- **Bauhaus & Material Design 3 Interface**: Zero-scroll responsive studio cockpit with auto-adapting Dark and Light themes.
- **Realtime Model Context Protocol (MCP)**: Native stdio & HTTP/SSE MCP server for LLMs and autonomous agents.
- **Google Colab & Cloud VPS Ready**: 1-click Colab notebook with instant Cloudflare HTTPS tunnel and secure API key authentication.
- **14 Aesthetic LoRA Style Presets**: Instant photoreal, cinematic 35mm, cyberpunk, anime studio, and octane 3D looks with custom prefix/suffix injections.
- **Integrated Analytics & KPI Dashboard**: Track lifetime generation speed, success rates, token usage, and project-based asset folders.

---

## 🚀 Quickstart

### Option 1: Google Colab (1-Click Cloud Run)
Run FlowGen completely free on Google's cloud with a single click:
1. Open [`FlowGen_Colab.ipynb`](FlowGen_Colab.ipynb) in Google Colab.
2. Run the cells to install Chromium and start the Cloudflare tunnel.
3. Access your live public URL and copy the generated `FLOWGEN_API_KEY`.

### Option 2: Local Installation (Windows / macOS / Linux)

```bash
# 1. Clone repository
git clone https://github.com/AliRash3ed/flowgen.git
cd flowgen/browser2api

# 2. Create virtual environment & install requirements
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
playwright install chromium

# 3. Launch Studio Interface
python run_hud.py
```
Open **[http://127.0.0.1:8787](http://127.0.0.1:8787)** in your browser.

### Option 3: Docker VPS Deployment

```bash
docker compose up -d
```
The studio will be available at `http://YOUR_SERVER_IP:8787`.

---

## 🤖 AI Agent MCP Setup

FlowGen enables AI Agents in **Claude Desktop**, **Cursor**, and **Antigravity** to act as creative directors and batch-generate visuals.

### Claude Desktop Configuration
Add this entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flowgen": {
      "command": "python",
      "args": ["/path/to/flowgen/browser2api/run_mcp.py"],
      "env": {
        "FLOWGEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Exposed MCP Tools
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `flow_generate` | `prompts`, `model`, `orientation`, `workers`, `style_suffix` | Submits batch generation and returns local file paths |
| `flow_get_status` | _none_ | Returns engine health, worker count, and active queue state |
| `flow_get_history` | _none_ | Returns historical analytics, image count, and daily trends |
| `flow_list_projects` | _none_ | Lists all project folders and generated image counts |
| `flow_list_styles` | _none_ | Returns available visual style presets |
| `flow_auth_status` | _none_ | Verifies active Google Flow session status |

---

## 🌐 REST API Usage

You can also dispatch generation jobs via standard HTTP requests:

```bash
curl -X POST "http://127.0.0.1:8787/api/batch/start" \
  -H "x-api-key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "A futuristic electric supercar doing a high-speed drift on neon wet city streets, cinematic iridescence",
      "Hyperrealistic crystal mountain peak at sunrise, volumetric morning mist"
    ],
    "project_name": "Tesla Cyberpunk",
    "model": "nano_banana_2_1",
    "orientation": "portrait",
    "workers": 2,
    "wait_for_completion": false
  }'
```

---

## 👨‍💻 Author & Credits

Architected & engineered by **Ali Bhatti** ([@alirash3ed](https://github.com/AliRash3ed)).
- **GitHub**: [@AliRash3ed](https://github.com/AliRash3ed)
- **LinkedIn**: [Ali Rasheed](https://www.linkedin.com/in/alirasheedbhatti/)
- **Instagram**: [@this_is_ali_r](https://www.instagram.com/this_is_ali_r/)

Built with Bauhaus geometric clarity, Material Design 3 elevation system, and parallel browser tab concurrency for high-throughput image production.
