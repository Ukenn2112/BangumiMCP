"""Bangumi MCP Server - Model Context Protocol server for Bangumi TV API."""
import asyncio
import atexit
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make the src/ directory importable as top-level modules for local stdio runs.
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Load environment variables from .env file
load_dotenv()
from server import get_mcp
from utils.api_client import close_http_client


def cleanup():
    """Cleanup function to close HTTP client on shutdown."""
    try:
        # Check if an event loop is currently running
        try:
            asyncio.get_running_loop()
            # If we get here, loop is running - we can't block, so return
            return
        except RuntimeError:
            # No running loop, safe to proceed with cleanup
            pass
        
        # Use asyncio.run() which handles event loop creation and cleanup
        asyncio.run(close_http_client())
    except Exception:
        # Best effort cleanup - fail silently
        pass


# Register cleanup handler
atexit.register(cleanup)

# --- Running the server ---

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    get_mcp().run(transport=transport)
