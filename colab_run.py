"""FlowGen Cloud & Google Colab 1-Click Remote Runner.

Run this script in Google Colab, Cloud Shell, or a remote Linux VPS:
1. Sets up virtual framebuffer (Xvfb) for headless Chromium execution
2. Launches FlowGen Studio on port 8787
3. Establishes a secure Cloudflare HTTPS Tunnel (no token/account needed)
4. Generates an API Key for LLM Agents (Claude Desktop, Cursor, Antigravity)
"""

import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


def setup_system():
    print("\n" + "=" * 65)
    print(" [*] FLOWGEN STUDIO - Google Colab / Cloud VPS Runner")
    print(" [*] Architected by Ali Bhatti (@alirash3ed)")
    print("=" * 65 + "\n")

    # Install packages if running in Colab
    if "google.colab" in sys.modules:
        print("[+] Detected Google Colab environment. Verifying dependencies...")
        subprocess.run(["apt-get", "update", "-qq"], check=False)
        subprocess.run(["apt-get", "install", "-qq", "-y", "xvfb", "libgbm-dev", "curl"], check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright", "fastapi", "uvicorn", "websockets", "pillow", "pydantic"], check=False)
        subprocess.run(["playwright", "install", "chromium"], check=False)


def setup_api_key() -> str:
    key = os.environ.get("FLOWGEN_API_KEY", "").strip()
    if not key:
        key = f"fg_live_{secrets.token_hex(16)}"
        os.environ["FLOWGEN_API_KEY"] = key
    print(f" [+] FlowGen API Key: {key}")
    return key


def start_tunnel(port: int = 8787) -> str:
    """Download and launch cloudflared to create an instant public HTTPS tunnel."""
    cloudflared = shutil.which("cloudflared")
    if not cloudflared:
        print("[+] Fetching cloudflared tunnel client...")
        if sys.platform == "linux":
            subprocess.run(["curl", "-sL", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-o", "cloudflared"], check=False)
            subprocess.run(["chmod", "+x", "cloudflared"], check=False)
            cloudflared = "./cloudflared"
        else:
            print("[!] On non-linux platform, please install cloudflared manually or run local port forward.")
            return f"http://127.0.0.1:{port}"

    log_path = Path("tunnel.log")
    if log_path.exists():
        log_path.unlink()

    print("[+] Launching Cloudflare HTTPS Tunnel...")
    proc = subprocess.Popen(
        [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    tunnel_url = None
    start_time = time.time()
    while time.time() - start_time < 30:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            break

    if tunnel_url:
        print(f"\n [🔥] FLOWGEN IS LIVE ON PUBLIC CLOUD:")
        print(f"      Dashboard: {tunnel_url}")
        return tunnel_url
    else:
        print("[!] Could not auto-detect tunnel URL within 30s. Check tunnel output.")
        return f"http://127.0.0.1:{port}"


def main():
    setup_system()
    api_key = setup_api_key()

    port = int(os.environ.get("FLOWGEN_PORT", 8787))

    # Start FlowGen HUD server
    print(f"[+] Starting FlowGen HUD server on 0.0.0.0:{port}...")
    server_cmd = [sys.executable, "browser2api/run_hud.py", "--host", "0.0.0.0", "--port", str(port), "--no-browser"]
    if not Path("browser2api/run_hud.py").exists() and Path("run_hud.py").exists():
        server_cmd = [sys.executable, "run_hud.py", "--host", "0.0.0.0", "--port", str(port), "--no-browser"]

    server_proc = subprocess.Popen(server_cmd)
    time.sleep(2)

    public_url = start_tunnel(port=port)

    print("\n" + "=" * 65)
    print(" [⭐] AI AGENT MCP CONFIGURATION (Paste into Claude Desktop / Cursor):")
    print("=" * 65)
    print(f"""
{{
  "mcpServers": {{
    "flowgen_cloud": {{
      "url": "{public_url}/api/mcp/sse",
      "headers": {{
        "x-api-key": "{api_key}"
      }}
    }}
  }}
}}
""")
    print("=" * 65)
    print(f" [*] REST API cURL Test:")
    print(f'     curl -X POST "{public_url}/api/batch/start" \\')
    print(f'          -H "x-api-key: {api_key}" \\')
    print('          -H "Content-Type: application/json" \\')
    print('          -d \'{"prompts": ["A futuristic electric supercar on neon wet streets"]}\'')
    print("=" * 65 + "\n")

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Shutting down FlowGen server...")
        server_proc.terminate()


if __name__ == "__main__":
    main()
