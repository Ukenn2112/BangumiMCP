"""Contract tests for the OpenAPI resource."""

import json
import unittest

from mcp.server.fastmcp import FastMCP

from src.resources.openapi_resource import register


class OpenAPIResourceTest(unittest.IsolatedAsyncioTestCase):
    async def test_resource_returns_openapi_document_without_content_envelope(self):
        server = FastMCP("test")
        register(server)

        contents = await server.read_resource("api://bangumi/openapi")
        document = json.loads(contents[0].content)

        self.assertEqual(document["openapi"], "3.0.3")
        self.assertIn("paths", document)
        self.assertFalse({"type", "text", "annotations"} <= document.keys())


if __name__ == "__main__":
    unittest.main()
