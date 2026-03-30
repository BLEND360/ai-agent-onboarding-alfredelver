import pytest

from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.fetchers.rss_fetcher import RSSFetcher
from src.transformers.article_transformer import ArticleTransformer
from src.storage.markdown_storage import MarkdownStorage


@pytest.mark.asyncio
async def test_both_fetchers():
    """Test both fetchers work."""
    # HackerNews
    transformer = ArticleTransformer()
    storage = MarkdownStorage()

    hn = HackerNewsFetcher(transformer, storage)
    hn_articles = await hn.fetch(limit=5)
    assert (
        len(hn_articles) > 0
    )  # assert is a debugging statement that checks if a condition is True.
    # If it's not, it raises an AssertionError and stops the program.

    # RSS
    rss = RSSFetcher("https://hnrss.org/frontpage", transformer, storage)
    rss_articles = await rss.fetch()
    assert len(rss_articles) > 0

    print(f"HN: {len(hn_articles)} articles")
    print(f"RSS: {len(rss_articles)} articles")


@pytest.mark.asyncio
async def test_concurrent_fetching():
    """Test fetching from both sources concurrently."""
    import asyncio
    import time

    transformer = ArticleTransformer()
    storage = MarkdownStorage()
    hn = HackerNewsFetcher(transformer, storage)
    rss = RSSFetcher("https://hnrss.org/frontpage", transformer, storage)

    start = time.time()

    # Fetch both at same time!
    hn_articles, rss_articles = await asyncio.gather(hn.fetch(limit=5), rss.fetch())

    elapsed = time.time() - start

    total = len(hn_articles) + len(rss_articles)
    print(f"Fetched {total} articles in {elapsed:.2f}s")

    assert elapsed < 10.0  # Should be fast with concurrent
