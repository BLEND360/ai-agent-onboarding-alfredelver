# Deployment Guide

## Local Deployment (Recommended for Learning)

This project is designed to run locally. No cloud deployment needed!

### Requirements

- macOS, Linux, or Windows (WSL supported)
- Python 3.11+
- 2GB RAM
- 1GB disk space

### Setup

See [README.md](../README.md) for full installation instructions.

### Running

```bash
# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run complete pipeline
python -m src.complete_pipeline

# Run individual stages
python -m src.main                    # Fetch only
python -m src.pipeline                # Fetch + Filter
python -m src.evaluation.evaluator    # Evaluate agent quality
```

### Scheduling

**macOS/Linux (cron):**

```bash
# Edit crontab
crontab -e

# Add line to run daily at 9 AM
0 9 * * * cd /path/to/ai-agent-onboarding && /path/to/venv/bin/python -m src.complete_pipeline
```

**Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9 AM
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `-m src.complete_pipeline`
7. Start in: `C:\path\to\ai-agent-onboarding`

## Docker (Optional)

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Pass API keys at runtime, not build time
CMD ["python", "-m", "src.complete_pipeline"]
```

**Build and run:**

```bash
docker build -t ai-agent-onboarding .
docker run --env-file .env -v $(pwd)/data:/app/data ai-agent-onboarding
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key (free tier: 5 req/min) |
| `NEWSAPI_KEY` | No | NewsAPI key (not currently used by fetchers) |

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

### Rate Limiting

The Gemini free tier allows 5 requests per minute. The codebase handles this:
- **Evaluator:** 13-second delay between LLM calls (`src/evaluation/evaluator.py`)
- **Fetchers:** Semaphore-based rate limiting (10 concurrent requests, `src/strategies/rate_limit_strategy.py`)

If you upgrade to a paid Gemini plan, you can reduce or remove the delays.

## Database

**Location:** `data/news_agent.db` (SQLite, created automatically on first run)

**Check article count:**

```bash
sqlite3 data/news_agent.db "SELECT COUNT(*) FROM articles;"
```

**Check sources:**

```bash
sqlite3 data/news_agent.db "SELECT source, COUNT(*) FROM articles GROUP BY source;"
```

**Reset database:**

```bash
rm data/news_agent.db
python -m src.complete_pipeline  # Recreates automatically
```

## MCP Server

The FastMCP database server runs as a subprocess (stdio transport) when invoked by skills or tests. No separate server process needed.

**Test it manually:**

```bash
python -m src.mcp.database_server
```

**Test via client:**

```bash
python -m src.skills.search_skill
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'src'`**
- Run scripts as modules: `python -m src.complete_pipeline` (not `python src/complete_pipeline.py`)
- Exception: MCP server is launched via `StdioServerParameters` with `-m` flag automatically

**API rate limits (429 RESOURCE_EXHAUSTED)**
- Wait 60 seconds and retry
- The Gemini free tier allows 5 requests per minute
- The evaluator already includes 13s delays between calls

**503 UNAVAILABLE from Gemini**
- Transient server-side issue, retry after a few minutes
- Not a code bug

**LLM returns bad JSON / filtering scores 0**
- Usually caused by rate limiting (API error falls back to `relevant: False`)
- Wait for rate limit to reset and re-run

**Tests failing with "async def functions are not natively supported"**
- Ensure `@pytest.mark.asyncio` decorator is on all async test functions
- Ensure `pytest-asyncio` is installed: `pip install pytest-asyncio`

**Database locked errors**
- Only one process should write to the database at a time
- Kill any background pipeline runs before starting a new one
