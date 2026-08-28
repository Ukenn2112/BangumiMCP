"""Bangumi MCP Server - Model Context Protocol server for Bangumi TV API."""
import asyncio
import atexit
import os

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

# Load environment variables from .env file
load_dotenv()

# Initialize MCPServer
mcp = MCPServer("bangumi-tv")

# Import and register all components
from src.resources import openapi_resource
from src.tools import (
    subject_tools,
    character_tools,
    person_tools,
    user_tools,
    collection_tools,
    revision_tools,
    index_tools,
)
from src.prompts import workflow_prompts
from src.utils.api_client import close_http_client

# Register resources
openapi_resource.register(mcp)

# Register tools (55 total)
subject_tools.register(mcp)
character_tools.register(mcp)
person_tools.register(mcp)
user_tools.register(mcp)
collection_tools.register(mcp)
revision_tools.register(mcp)
index_tools.register(mcp)

# Register prompts
workflow_prompts.register(mcp)


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
    mcp.run(transport=transport)
