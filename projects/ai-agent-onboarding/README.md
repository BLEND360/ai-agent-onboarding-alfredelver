# AI Agent Onboarding Project

**Multi-agent news aggregation system with FastMCP integration**

A production-ready AI agent pipeline that fetches, filters, summarizes, and writes AI/ML news newsletters using async Python, SOLID principles, and Google Gemini.

## Features

- **Async News Fetching** from 3 sources (HackerNews API, RSS feeds, GitHub Trending)
- **AI-Powered Filtering** using Google Gemini 2.5 Flash with relevance scoring
- **FastMCP Integration** for database tools with auto-generated schemas
- **Multi-Agent Pipeline** (Filter -> Summarize -> Write)
- **SQLite Database** with async access via aiosqlite
- **Reusable Skills** (SearchSkill over MCP)
- **Evaluation Framework** with precision, recall, F1 metrics
- **SOLID Design** with Template Method, Factory, Strategy patterns

## Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key (free tier works)

### Installation

```bash
# Clone repo
git clone https://github.com/your-org/ai-agent-onboarding.git
cd ai-agent-onboarding

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run Complete Pipeline

```bash
python -m src.complete_pipeline
```

This runs all 5 stages:
1. Fetches articles from HackerNews, RSS, and GitHub Trending
2. Saves to SQLite database
3. Filters for AI/ML relevance with Gemini
4. Summarizes by topic
5. Writes final newsletter

Output files:
- `data/articles/` - Raw fetched articles (markdown)
- `data/context/filtered_articles.md` - AI-filtered articles
- `data/context/summary.md` - Topic summaries
- `data/output/newsletter.md` - Final newsletter

### Run Individual Components

```bash
# Fetch articles only
python -m src.main

# Fetch + Filter pipeline
python -m src.pipeline

# Evaluate filtering quality
python -m src.evaluation.evaluator

# Test MCP database server
python -m src.mcp.database_server

# Test search skill
python -m src.skills.search_skill
```

## Architecture

```
+---------------------------------------------+
|         News Sources                         |
|  HackerNews | RSS Feeds | GitHub Trending    |
+---------------------+-----------------------+
                      |
                      v
           +--------------------+
           | FetchOrchestrator  |
           |   (Milestone 1-2)  |
           +----------+---------+
                      |
                      v
          +-----------+-----------+
          |  SQLite Database      |  <-- FastMCP Server
          |  (aiosqlite)          |      (query, search, get_sources)
          +-----------+-----------+
                      |
                      v
          +-----------+-----------+
          |  NewsFilterAgent      |
          |  (Gemini + Tools)     |
          +-----------+-----------+
                      |
                      v
          +-----------+-----------+
          |  SummarizerAgent      |
          |  (+ SearchSkill/MCP)  |
          +-----------+-----------+
                      |
                      v
          +-----------+-----------+
          |  WriterAgent          |
          |  (Newsletter output)  |
          +-----------+-----------+
                      |
                      v
              newsletter.md
```

## Project Structure

```
ai-agent-onboarding/
├── src/
│   ├── agents/                  # AI agents (Template Method pattern)
│   │   ├── base_agent.py        # Abstract base with execute() lifecycle
│   │   ├── news_filter_agent.py # Filters articles by AI/ML relevance
│   │   ├── enhanced_filter_agent.py # Filter + Gemini function calling
│   │   ├── summarizer_agent.py  # Groups and summarizes by topic
│   │   └── writer_agent.py      # Generates final newsletter
│   ├── fetchers/                # News source fetchers
│   │   ├── base_fetcher.py      # Abstract base (Template Method)
│   │   ├── interfaces.py        # AuthenticatedFetcher, PaginatedFetcher
│   │   ├── hackernews_fetcher.py
│   │   ├── rss_fetcher.py
│   │   └── github_trending_fetcher.py
│   ├── mcp/                     # FastMCP servers
│   │   ├── database_server.py   # Database tools (FastMCP edition)
│   │   ├── hello_server.py      # Simple FastMCP example
│   │   └── simple_client.py     # MCP client
│   ├── skills/                  # Higher-level abstractions over MCP
│   │   └── search_skill.py      # Article search via MCP
│   ├── database/
│   │   └── db_manager.py        # Async SQLite manager
│   ├── models/
│   │   └── articles.py          # Article dataclass
│   ├── storage/
│   │   ├── base_storage.py      # Abstract storage interface
│   │   └── markdown_storage.py  # Markdown file storage
│   ├── transformers/
│   │   └── article_transformer.py # Raw data -> Article objects
│   ├── factories/
│   │   └── fetcher_factory.py   # Factory pattern for fetchers
│   ├── strategies/
│   │   └── rate_limit_strategy.py # Semaphore + TokenBucket strategies
│   ├── tools/                   # Agent tools (Gemini function calling)
│   │   ├── calculator.py        # Math expression evaluator
│   │   └── websearch.py         # Web search (mock)
│   ├── utils/
│   │   └── rate_limiter.py      # Async rate limiting
│   ├── evaluation/
│   │   └── evaluator.py         # Golden dataset evaluation
│   ├── main.py                  # Fetch-only entry point
│   ├── pipeline.py              # Fetch + Filter pipeline
│   ├── complete_pipeline.py     # Full 5-stage pipeline
│   └── orchestrator.py          # Fetcher orchestration (DIP)
├── tests/                       # 15 test files, 23+ tests
├── data/
│   ├── articles/                # Fetched articles (markdown)
│   ├── context/                 # Filtered + summarized output
│   ├── output/                  # Final newsletter
│   └── evaluation/              # Golden dataset + reports
├── docs/
│   └── design-decisions.md      # SOLID principles documentation
├── requirements.txt
├── conftest.py
└── .env
```

## Key Technologies

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Async/await, type hints |
| **aiohttp** | Async HTTP for API calls |
| **google-genai** | Google Gemini 2.5 Flash LLM |
| **FastMCP** (`mcp.server.fastmcp`) | MCP server with auto-generated tool schemas |
| **aiosqlite** | Async SQLite database |
| **feedparser** | RSS feed parsing |
| **BeautifulSoup** | GitHub Trending scraping |
| **pytest + pytest-asyncio** | Async test framework |

## Design Patterns

| Pattern | Where | Example |
|---|---|---|
| **Template Method** | `BaseAgent.execute()`, `BaseFetcher.fetch_and_save()` | Skeleton algorithm with customization points |
| **Factory** | `FetcherFactory.create()` | Create fetchers by source type string |
| **Strategy** | `SemaphoreStrategy`, `TokenBucketStrategy` | Swappable rate limiting approaches |
| **Dependency Injection** | `FetchOrchestrator(fetchers, storage, transformer)` | Constructor injection, testable with mocks |

## FastMCP Integration (Milestone 4)

The MCP server uses **FastMCP** which auto-generates JSON schemas from Python type hints and docstrings -- no manual schema definitions needed:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("database-server")

@mcp.tool()
async def search_articles(query: str, limit: int = 20) -> str:
    """Search articles by keyword in title or summary."""
    # FastMCP generates the tool schema automatically
    ...

@mcp.resource("articles://recent")
async def recent_articles() -> str:
    """Get the 10 most recent articles."""
    ...
```

**MCP Tools:** `query_articles`, `search_articles`, `get_sources`
**MCP Resources:** `articles://recent`

## Milestones

- Milestone 0: Project setup and environment
- Milestone 1: Async news fetcher (HackerNews, RSS, GitHub Trending)
- Milestone 2: SOLID refactoring (DIP, Template Method, Factory, Strategy)
- Milestone 3: AI agent with Gemini + tool use (filter, calculator, search)
- Milestone 4: FastMCP-powered pipeline with database server and skills
- Milestone 5: Evaluation framework with golden dataset

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Evaluation

The evaluation framework tests the NewsFilterAgent against a golden dataset of 10 hand-labeled articles (5 relevant, 5 not):

```bash
python -m src.evaluation.evaluator
```

Metrics: Accuracy, Precision, Recall, F1 Score
Report: `data/evaluation/evaluation_report.md`

Note: The evaluator includes 13-second delays between API calls to respect the Gemini free-tier rate limit (5 req/min).

## License

MIT

## Acknowledgments

Built as part of AI Agent Onboarding curriculum (v3.3).
