"""Model Context Protocol (MCP) Server for FlowGen Studio.
Enables AI Agents (Claude Desktop, Cursor, Antigravity, etc.) to generate unlimited images via Google Flow.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from .config import DATA_DIR
from .history import tracker
from .platforms.flow.auth import check_active_login, has_saved_session
from .platforms.flow.enums import FlowCount, FlowModel, FlowOrientation
from .platforms.flow.multiworker import FlowOrchestrator

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger("flowgen-mcp")

DEFAULT_OUTPUT_DIR = Path("E:/Organized/flowgen/browser2api/output")
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


TOOLS = [
    {
        "name": "flow_generate",
        "description": "Generate high-quality images via Google Flow using parallel browser workers. Returns saved local filepaths and metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of prompt strings to generate images for."
                },
                "model": {
                    "type": "string",
                    "enum": ["nano_banana_2_1", "nano_banana_pro", "nano_banana_2_lite"],
                    "default": "nano_banana_2_1",
                    "description": "Google Flow generation model to use."
                },
                "orientation": {
                    "type": "string",
                    "enum": ["portrait", "landscape"],
                    "default": "portrait",
                    "description": "Aspect ratio orientation (portrait=9:16, landscape=16:9)."
                },
                "workers": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "default": 2,
                    "description": "Number of concurrent browser tab workers to run in parallel."
                },
                "headless": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to run Chrome in headless mode."
                },
                "style_suffix": {
                    "type": "string",
                    "default": "",
                    "description": "Optional artistic style suffix to append to each prompt (e.g. 'cinematic raw photography, 35mm')."
                }
            },
            "required": ["prompts"]
        }
    },
    {
        "name": "flow_get_status",
        "description": "Get current FlowGen engine telemetry, active workers count, and queue status.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "flow_get_history",
        "description": "Get historical analytics: total images generated, daily trends, and recent projects.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "flow_auth_status",
        "description": "Check if a valid Google Flow session is logged in and ready for generation.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "flow_list_projects",
        "description": "List all output project folders and image counts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "flow_list_styles",
        "description": "List all available aesthetic LoRA and visual style presets (cinematic, cyberpunk, anime, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


async def handle_tool_call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Execute an MCP tool call."""
    if name == "flow_auth_status":
        has_session = has_saved_session()
        return {
            "has_saved_session": has_session,
            "status": "ready" if has_session else "login_required",
            "profile_dir": str(DATA_DIR / "browser_data" / "flow_cdp")
        }

    elif name == "flow_list_projects":
        stats = tracker.get_analytics()
        return {"projects": stats.get("projects", [])}

    elif name == "flow_list_styles":
        return {
            "styles": [
                {"id": "cinematic", "name": "Cinematic raw", "desc": "35mm film, rim light"},
                {"id": "cyberpunk", "name": "Cyberpunk neon", "desc": "Teal and magenta wet streets"},
                {"id": "anime", "name": "Anime studio", "desc": "Makoto Shinkai atmosphere"},
                {"id": "dark_fantasy", "name": "Dark fantasy", "desc": "Eldritch gothic atmosphere"},
                {"id": "octane_3d", "name": "Octane 3D render", "desc": "Subsurface scattering & glass"},
                {"id": "oil_painting", "name": "Impressionist oil", "desc": "Heavy textured palette knife"},
                {"id": "vector", "name": "Vector graphic", "desc": "Clean isometric geometric"},
                {"id": "vintage", "name": "Vintage 1970s", "desc": "Kodachrome analog grain"},
                {"id": "synthwave", "name": "Synthwave 80s", "desc": "Retrogrid sunset & neon"}
            ]
        }

    elif name == "flow_get_history":
        stats = tracker.get_analytics()
        return stats

    elif name == "flow_get_status":
        return {
            "engine": "FlowGen Studio v2.4",
            "status": "online",
            "output_dir": str(DEFAULT_OUTPUT_DIR),
            "auth_ready": has_saved_session(),
        }

    elif name == "flow_generate":
        prompts = args.get("prompts", [])
        if not prompts:
            raise ValueError("At least one prompt is required.")

        model_str = args.get("model", "nano_banana_2_1")
        orientation_str = args.get("orientation", "portrait")
        workers = min(max(args.get("workers", 2), 1), 4)
        headless = args.get("headless", True)
        style_suffix = args.get("style_suffix", "")

        model_enum = FlowModel(model_str) if model_str in [m.value for m in FlowModel] else FlowModel.NANO_BANANA_2_1
        orient_enum = FlowOrientation(orientation_str) if orientation_str in [o.value for o in FlowOrientation] else FlowOrientation.PORTRAIT

        orch = FlowOrchestrator(
            output_dir=DEFAULT_OUTPUT_DIR,
            max_workers=workers,
            headless=headless,
            model=model_enum,
            orientation=orient_enum,
            count=FlowCount.X1,
            style_suffix=style_suffix,
        )
        orch.set_prompts(prompts)

        # Run synchronously to completion for agent
        t0 = asyncio.get_event_loop().time()
        await orch.start()

        # Wait until finished
        while orch.state == "running":
            await asyncio.sleep(0.5)

        duration = asyncio.get_event_loop().time() - t0
        images = orch.generated_gallery

        # Record in history tracker
        tracker.record_batch_completed(
            batch_id=f"batch_{int(t0)}",
            prompts=prompts,
            model=model_str,
            orientation=orientation_str,
            workers=workers,
            duration_seconds=duration,
            generated_images=images,
            status="completed" if images else "failed"
        )

        return {
            "status": "completed",
            "prompts_count": len(prompts),
            "images_count": len(images),
            "duration_seconds": round(duration, 1),
            "images": [
                {
                    "filename": img.get("filename"),
                    "local_path": img.get("local_path"),
                    "prompt": img.get("prompt"),
                    "duration_ms": img.get("duration_ms")
                }
                for img in images
            ]
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


async def run_mcp_server():
    """Main JSON-RPC 2.0 loop reading from stdin and writing to stdout."""
    while True:
        line_str = await asyncio.to_thread(sys.stdin.readline)
        if not line_str:
            break

        line_str = line_str.strip()
        if not line_str:
            continue

        try:
            req = json.loads(line_str)
            msg_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "flowgen-mcp", "version": "2.4.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                try:
                    result_data = await handle_tool_call(tool_name, tool_args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result_data, indent=2)}]
                        }
                    }
                except Exception as exc:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32000, "message": str(exc)}
                    }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method {method} not found"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
