import pytest

from src.orchestrator import FetchOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_fetch_all():
    "Testing orchestrator is fetching from all sources"
    orc = FetchOrchestrator()
    articles = await orc.fetch_all()

    assert len(articles) > 0

    # should have different sources
    sources = {a.source for a in articles}
    assert len(sources) > 1
