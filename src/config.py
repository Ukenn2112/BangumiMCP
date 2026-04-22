"""Configuration constants for Bangumi MCP server."""
import os

# API Configuration
BANGUMI_API_BASE = "https://api.bgm.tv"
USER_AGENT = "BangumiMCP/1.0.0 (https://github.com/Ukenn2112/BangumiMCP)"
# Local stdio fallback only; public Worker requests use request-scoped tokens.
BANGUMI_TOKEN = os.getenv("BANGUMI_TOKEN")
