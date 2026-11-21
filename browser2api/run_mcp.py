"""Launcher for the FlowGen MCP Server (Model Context Protocol).
Connect this script in your Claude Desktop or Cursor MCP configuration!
"""

import asyncio
import sys
from pathlib import Path

# Ensure src is in python path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from browser2api.mcp_server import run_mcp_server

if __name__ == "__main__":
    asyncio.run(run_mcp_server())
