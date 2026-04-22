"""Shared MCP server setup."""

from functools import cache


@cache
def get_mcp():
    from mcp.server.fastmcp import FastMCP
    from prompts import workflow_prompts
    from resources import openapi_resource
    from tools import (
        character_tools,
        collection_tools,
        index_tools,
        person_tools,
        revision_tools,
        subject_tools,
        user_tools,
    )

    mcp = FastMCP(
        "bangumi-tv",
        host="0.0.0.0",
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
    )

    openapi_resource.register(mcp)
    subject_tools.register(mcp)
    character_tools.register(mcp)
    person_tools.register(mcp)
    user_tools.register(mcp)
    collection_tools.register(mcp)
    revision_tools.register(mcp)
    index_tools.register(mcp)
    workflow_prompts.register(mcp)
    return mcp
