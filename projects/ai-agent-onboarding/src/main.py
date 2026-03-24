"""Main entry point for news fetcher."""
import asyncio
import sys
from src.orchestrator import FetchOrchestrator
from src.transformers.article_transformer import ArticleTransformer
from src.storage.markdown_storage import MarkdownStorage
from src.fetchers.github_trending_fetcher import GithubTrendingFetcher
from src.fetchers.hackernews_fetcher import HackerNewsFetcher

# async def main():
#     """Main function."""
#     print("=" * 60)
#     print("  AI Agent Onboarding - News Fetcher")
#     print("  Milestone 1: Async News Fetcher")
#     print("=" * 60)

#     try:
#         # Run orchestrator
#         transformer = ArticleTransformer()
#         storage = MarkdownStorage()
#         orchestrator = FetchOrchestrator(transformer, storage)
#         articles = await orchestrator.fetch_all()
        
#         print("\n" + "=" * 60)
#         print(f"Success! Fetched {len(articles)} articles total")
#         print(f"Saved to: data/articles/all_articles.md")
#         print("=" * 60)
        
#         return 0
    
#     except Exception as e:
#         print(f"\nError: {e}")
#         import traceback
#         traceback.print_exc()
#         return 1

async def main():
    """Main entry point with dependency injection."""
    
    # Create dependencies
    transformer = ArticleTransformer()
    storage = MarkdownStorage("data/articles")
    
    # Create fetchers
    fetchers = [
        HackerNewsFetcher(transformer, storage),
        GithubTrendingFetcher(transformer, storage),
    ]
    
    # Inject dependencies into orchestrator
    orchestrator = FetchOrchestrator(
        fetchers=fetchers,
        storage=storage,
        transformer=transformer
    )
    
    # Run
    articles = await orchestrator.fetch_all()
    print(f" Fetched {len(articles)} articles total")

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

