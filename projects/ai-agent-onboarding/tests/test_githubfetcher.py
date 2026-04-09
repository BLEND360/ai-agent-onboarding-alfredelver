from src.fetchers.github_trending_fetcher import GithubTrendingFetcher
from src.transformers.article_transformer import ArticleTransformer
from src.storage.markdown_storage import MarkdownStorage
import asyncio
import pytest


@pytest.mark.asyncio
async def test_github():
    transformer = ArticleTransformer()
    storage = MarkdownStorage()

    fetcher = GithubTrendingFetcher(transformer, storage)
    articles = await fetcher.fetch_and_save()

    print(f"✅ Fetched {len(articles)} trending repos!")
    print(f"First: {articles[0].title}")


if __name__ == "__main__":
    asyncio.run(test_github())
