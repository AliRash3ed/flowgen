"""Google Flow account authentication and session status utilities."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable

from ...browser import BrowserManager
from ...config import DATA_DIR
from ...types import Platform
from .login import FlowLoginHandler
from .selectors import TOOL_URL

logger = logging.getLogger(__name__)


def get_flow_profile_dir() -> Path:
    """Get the path to Flow's persistent Chrome CDP profile directory."""
    return DATA_DIR / "browser_data" / f"{Platform.FLOW.value}_cdp"


def has_saved_session() -> bool:
    """Check if a persistent user profile exists for Google Flow."""
    profile_dir = get_flow_profile_dir()
    if not profile_dir.exists():
        return False
    # Check if Default or Cookies exist
    default_dir = profile_dir / "Default"
    return default_dir.exists()


async def check_active_login() -> dict[str, Any]:
    """Launch a quick headless check to verify if the Google Flow session is logged in."""
    if not has_saved_session():
        return {"logged_in": False, "reason": "No profile directory found"}

    bm = BrowserManager()
    try:
        context, page = await bm.launch_for_generation(Platform.FLOW, headless=True)
        handler = FlowLoginHandler()
        await page.goto(TOOL_URL, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        is_logged_in = await handler._check_ui_logged_in(page)

        avatar_url = None
        if is_logged_in:
            try:
                avatar_url = await page.evaluate("""() => {
                    const img = document.querySelector('img[aria-label*="Google Account"]') ||
                                document.querySelector('img[src*="googleusercontent.com/a/"]');
                    return img ? img.src : null;
                }""")
            except Exception:
                pass

        await bm.close()
        return {
            "logged_in": is_logged_in,
            "avatar_url": avatar_url,
        }
    except Exception as e:
        logger.warning(f"Error checking active login: {e}")
        try:
            await bm.close()
        except Exception:
            pass
        return {"logged_in": False, "error": str(e)}


async def interactive_login(
    on_update: Callable[[str], None] | None = None,
    timeout_seconds: int = 300,
) -> bool:
    """Launch a headed Chrome browser for user to sign in to Google Flow."""
    bm = BrowserManager()
    handler = FlowLoginHandler()

    try:
        if on_update:
            on_update("Opening Chrome window for Google Sign-in...")

        context, page = await bm.launch_for_login(Platform.FLOW)
        await page.goto(TOOL_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        if await handler._check_ui_logged_in(page):
            if on_update:
                on_update("Already logged in to Google Flow!")
            await asyncio.sleep(2)
            await bm.close()
            return True

        if on_update:
            on_update("Please sign in with your Google account in the browser window...")

        for i in range(timeout_seconds):
            await asyncio.sleep(1)
            if await handler._check_ui_logged_in(page):
                if on_update:
                    on_update("Google Flow login detected! Saving session...")
                await asyncio.sleep(3)
                await bm.close()
                return True

            if i % 15 == 0 and i > 0 and on_update:
                remaining = timeout_seconds - i
                on_update(f"Waiting for sign-in ({remaining}s remaining)...")

        if on_update:
            on_update("Login timed out.")
        await bm.close()
        return False

    except Exception as e:
        logger.error(f"Error during interactive login: {e}")
        try:
            await bm.close()
        except Exception:
            pass
        return False
