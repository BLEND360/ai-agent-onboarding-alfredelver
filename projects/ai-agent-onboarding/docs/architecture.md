# Architecture Documentation

## System Overview

Multi-agent AI system that fetches news from multiple sources, filters for AI/ML relevance using Google Gemini, and produces a daily newsletter. Built with async Python, SOLID principles, and FastMCP for tool integration.

## Design Principles

### 1. SOLID Principles

**Single Responsibility:**
- `ArticleTransformer` -- data transformation only
- `MarkdownStorage` -- file persistence only
- Each agent has one job (filter, summarize, write)
- Each fetcher handles one source

**Open/Closed:**
- `GithubTrendingFetcher` was added with zero changes to existing code
- New sources extend `BaseFetcher`, new agents extend `BaseAgent`

**Liskov Substitution:**
- All fetchers are interchangeable (verified in `tests/test_substitubality.py`)
- `FetchOrchestrator` works with any `BaseFetcher` implementation

**Interface Segregation:**
- `BaseFetcher` requires only 2 methods: `fetch_articles()`, `get_source_name()`
- Optional interfaces: `AuthenticatedFetcher`, `PaginatedFetcher` in `src/fetchers/interfaces.py`

**Dependency Inversion:**
- `FetchOrchestrator` depends on abstractions (`BaseFetcher`, `ArticleStorage`), not concrete classes
- All dependencies injected via constructors
- Easily testable with mocks (see `tests/test_orchestrator.py`)

### 2. Design Patterns

**Template Method** (`src/fetchers/base_fetcher.py`, `src/agents/base_agent.py`):
- `BaseFetcher.fetch_and_save()` defines: fetch -> save
- `BaseAgent.execute()` defines: load -> process -> save
- Subclasses customize the varying steps

**Factory** (`src/factories/fetcher_factory.py`):
- `FetcherFactory.create("hackernews", transformer, storage)` returns the right fetcher
- Registry-based: `_fetchers = {"hackernews": HackerNewsFetcher, "github": GithubTrendingFetcher}`

**Strategy** (`src/strategies/rate_limit_strategy.py`):
- `SemaphoreStrategy` -- limits concurrent requests via asyncio.Semaphore
- `TokenBucketStrategy` -- time-based rate limiting
- Injected into fetchers at construction time

### 3. Async-First

- All I/O is async (aiohttp, aiosqlite)
- Concurrent fetching with `asyncio.gather()`
- Non-blocking database operations
- Async MCP communication via stdio

## Component Details

### 1. Fetchers (Milestone 1)

**Purpose:** Fetch articles from external sources asynchronously.

| Fetcher | Source | Method |
|---|---|---|
| `HackerNewsFetcher` | HackerNews Firebase API | REST API, concurrent item fetching |
| `RSSFetcher` | Any RSS feed URL | feedparser library |
| `GithubTrendingFetcher` | GitHub Trending page | BeautifulSoup web scraping |

**Key Features:**
- Rate limiting via Strategy pattern (SemaphoreStrategy default: 10 concurrent)
- Error handling with graceful degradation
- Markdown output via MarkdownStorage
- Article normalization via ArticleTransformer

### 2. Agents (Milestones 3-4)

**BaseAgent** (`src/agents/base_agent.py`):
- Template Method: `execute()` -> `_load_context()` -> `_process()` -> `_save_result()`
- LLM: Google Gemini 2.5 Flash via `google-genai` SDK
- Tool support: Optional Gemini function calling via `_call_llm_with_tools()`

**NewsFilterAgent** (`src/agents/news_filter_agent.py`):
- Calls `_judge_relevance()` per article with structured JSON prompt
- Parses LLM response as JSON (handles ```json wrapping)
- Relevance threshold: 6/10
- Defaults to "not relevant" on API errors (safe fallback)

**EnhancedFilterAgent** (`src/agents/enhanced_filter_agent.py`):
- Extends NewsFilterAgent with Gemini function calling
- Registered tools: calculator, web_search
- Demonstrates tool-augmented agent pattern

**SummarizerAgent** (`src/agents/summarizer_agent.py`):
- Groups filtered articles by topic (key_topics field)
- Generates 2-3 sentence summaries per topic
- Can use SearchSkill for additional context via MCP

**WriterAgent** (`src/agents/writer_agent.py`):
- Final pipeline stage
- Generates newsletter with intro, organized content, conclusion
- Professional + friendly tone

### 3. FastMCP Integration (Milestone 4)

**Why FastMCP over regular MCP:**
- Auto-generates JSON tool schemas from Python type hints and docstrings
- No manual schema definitions needed
- Cleaner code: `@mcp.tool()` decorator instead of manual handler registration
- Resources via `@mcp.resource()` for read-only data access

**Database MCP Server** (`src/mcp/database_server.py`):

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("database-server")

@mcp.tool()
async def query_articles(source: Optional[str] = None, limit: int = 20) -> str:
    """Query articles from database with optional filters."""
    ...

@mcp.tool()
async def search_articles(query: str, limit: int = 20) -> str:
    """Search articles by keyword in title or summary."""
    ...

@mcp.tool()
async def get_sources() -> str:
    """Get list of all available article sources in the database."""
    ...

@mcp.resource("articles://recent")
async def recent_articles() -> str:
    """Get the 10 most recent articles."""
    ...
```

**SearchSkill** (`src/skills/search_skill.py`):
- Higher-level abstraction over MCP tools
- Connects to database_server via stdio transport
- Pattern: `StdioServerParameters` -> `stdio_client()` -> `ClientSession` -> `call_tool()`
- Returns structured dict with success flag, total, articles

### 4. Database

**DatabaseManager** (`src/database/db_manager.py`):
- Async SQLite via aiosqlite
- Schema: articles table with title, url (unique), source, published_at, summary, score, relevance_score
- Indexes on source and published_at
- Methods: initialize, insert_article, query_articles, search_articles, get_sources
- Duplicate URL handling via IntegrityError catch

### 5. Pipeline Orchestration

**FetchOrchestrator** (`src/orchestrator.py`):
- Dependency injection: `__init__(fetchers, storage, transformer)`
- `fetch_all()` iterates fetchers sequentially, collects all articles

**Complete Pipeline** (`src/complete_pipeline.py`):

```
Step 1: Fetch     -> HackerNews + RSS + GitHub -> data/articles/
Step 2: Database  -> Insert articles into SQLite
Step 3: Filter    -> NewsFilterAgent -> data/context/filtered_articles.md
Step 4: Summarize -> SummarizerAgent -> data/context/summary.md
Step 5: Write     -> WriterAgent -> data/output/newsletter.md
```

### 6. Evaluation (Milestone 5)

**FilterEvaluator** (`src/evaluation/evaluator.py`):
- Golden dataset: 10 hand-labeled test cases (5 relevant, 5 not)
- Located at: `data/evaluation/golden_dataset.json`
- Metrics: Accuracy, Precision, Recall, F1 Score
- Rate-limited: 13s delay between API calls (Gemini free tier: 5 req/min)
- Output: `data/evaluation/evaluation_report.md`

## Data Flow

```
1. External APIs (HackerNews, RSS, GitHub)
   |
2. Fetchers (async, rate-limited)
   |
3. ArticleTransformer (normalize to Article dataclass)
   |
4. MarkdownStorage (save raw articles) + DatabaseManager (SQLite)
   |
5. NewsFilterAgent (Gemini judges relevance, threshold >= 6/10)
   |
6. SummarizerAgent (groups by topic, generates summaries)
   |
7. WriterAgent (creates newsletter)
   |
8. data/output/newsletter.md
```

## Technology Choices

| Choice | Rationale |
|---|---|
| **Python 3.11+** | Native async/await, type hints, rich AI ecosystem |
| **Google Gemini** | Free tier (5 req/min), function calling support, fast inference |
| **FastMCP** | Auto-schema generation, cleaner than manual MCP, industry-standard protocol |
| **SQLite + aiosqlite** | No server needed, async access, easy deployment |
| **Markdown output** | Human-readable, git-friendly, easy to debug |

## Performance

| Operation | Time |
|---|---|
| Fetch 30+ articles (3 sources) | ~2-3 seconds |
| Filter 30 articles (Gemini) | ~30-45 seconds |
| Complete pipeline | ~2-3 minutes |
| Evaluation (10 cases, rate-limited) | ~2 minutes |

**Bottleneck:** Gemini API rate limits on free tier (5 req/min).

## Security

- **API keys** stored in `.env`, loaded via `python-dotenv`, never committed
- **SQL injection** prevented with parameterized queries throughout
- **LLM output** parsed safely with JSON validation and fallback defaults
- **Rate limiting** prevents API abuse (semaphore-based)

## Future Enhancements

- More sources (Twitter, Reddit, arXiv)
- Larger golden dataset for evaluation
- Docker deployment with scheduled runs
- Semantic search over article embeddings
- Web interface for newsletter browsing
