"""Test database MCP server (FastMCP edition)."""

import asyncio
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_database_server():
    """Test database MCP server."""
    print("Connecting to database server...")

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp.database_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"\nDatabase tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Get sources
            print(f"\nGetting sources...")
            result = await session.call_tool("get_sources", {})
            print(f"   {result.content[0].text[:200]}")

            # Query articles
            print(f"\nQuerying articles...")
            result = await session.call_tool("query_articles", {"limit": 5})
            print(f"   {result.content[0].text[:300]}")

            # Search
            print(f"\nSearching for 'AI'...")
            result = await session.call_tool(
                "search_articles",
                {
                    "query": "AI",
                    "limit": 3,
                },
            )
            print(f"   {result.content[0].text[:300]}")

            # Read resource (FastMCP bonus)
            print(f"\nReading 'articles://recent' resource...")
            try:
                resource = await session.read_resource("articles://recent")
                print(f"   {str(resource.contents[0])[:200]}")
            except Exception as e:
                print(f"   Resource read skipped: {e}")

            print("\nDatabase MCP server working!")


if __name__ == "__main__":
    asyncio.run(test_database_server())
