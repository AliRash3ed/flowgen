"""Launch the FlowGen HUD Studio Web Interface."""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure package root is in sys.path
package_root = Path(__file__).resolve().parent / "src"
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

from browser2api.gui.server import start_gui_server


def open_browser(url: str, delay: float = 1.2):
    """Wait for server to start, then open in user default browser."""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    parser = argparse.ArgumentParser(description="Launch the FlowGen Gaming HUD Workspace")
    parser.add_argument("--host", default="127.0.0.1", help="Host IP to bind to")
    parser.add_argument("--port", type=int, default=8787, help="Port to bind to (default: 8787)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open default browser")

    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    url = f"http://{args.host}:{args.port}"
    print("\n" + "=" * 65)
    print(" [*] FLOWGEN HUD STUDIO - Multi-Worker Google Flow Interface")
    print(f" [+] Access HUD at: {url}")
    print("=" * 65 + "\n")

    if not args.no_browser:
        threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    start_gui_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
