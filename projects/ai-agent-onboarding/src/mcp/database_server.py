"""Database MCP server using FastMCP.

Provides tools to query the article database.
FastMCP auto-generates schemas from type hints and docstrings.
"""

import asyncio
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from src.database.db_manager import DatabaseManager

# Create FastMCP server
mcp = FastMCP("database-server")

# Shared database manager instance
db = DatabaseManager()
_db_initialized = False


async def _ensure_db():
    """Initialize DB on first use."""
    global _db_initialized
    if not _db_initialized:
        await db.initialize()
        _db_initialized = True


# ---------- Tools ----------
# Each decorated function = one MCP tool.
# FastMCP reads the function signature + docstring to build the JSON schema.


@mcp.tool()
async def query_articles(source: Optional[str] = None, limit: int = 20) -> str:
    """Query articles from database with optional filters.

    Args:
        source: Filter by source (e.g., 'hackernews', 'rss'). Omit for all sources.
        limit: Maximum number of articles to return (default 50).
    """

    await _ensure_db()

    articles = await db.query_articles(source=source, limit=limit)

    result = {
        "total": len(articles),
        "articles": articles[:10],  # First 10 full, rest just counted
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_articles(query: str, limit: int = 20) -> str:
    """Search articles by keyword in title or summary.

    Args:
        query: Search query (searches in title and summary).
        limit: Maximum results to return (default 20).
    """
    await _ensure_db()

    articles = await db.search_articles(query=query, limit=limit)

    result = {
        "total": len(articles),
        "query": query,
        "articles": articles,
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_sources() -> str:
    """Get list of all available article sources in the database."""
    await _ensure_db()

    sources = await db.get_sources()

    result = {
        "sources": sources,
        "total": len(sources),
    }
    return json.dumps(result, indent=2)


# ---------- Resources (bonus FastMCP feature) ----------
# Resources let clients read data without calling a tool.
# Think of them as GET endpoints.


@mcp.resource("articles://recent")
async def recent_articles() -> str:
    """Get the 10 most recent articles."""
    await _ensure_db()
    articles = await db.query_articles(limit=10)
    return json.dumps(articles, indent=2)


# ---------- Run ----------

if __name__ == "__main__":
    print(" Database MCP Server starting...")
    print(" Tools: query_articles, search_articles, get_sources")
    mcp.run()
