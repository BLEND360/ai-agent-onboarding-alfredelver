"""Orchestrate multiple news fetchers."""
import asyncio
from typing import List
from src.models.articles import Article
from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.fetchers.rss_fetcher import RSSFetcher
from src.fetchers.github_trending_fetcher import GithubTrendingFetcher

class FetchOrchestrator:
    """
    Orchestrates fetching from multiple sources.
    
    Coordinates HackerNews, RSS, and other fetchers.
    """
    
    def __init__(self, transformer, storage):
        """Initialize orchestrator with all fetchers."""
        self.storage = storage
        self.fetchers = [
            ('HackerNews', HackerNewsFetcher(transformer, storage)),
            ('HN RSS', RSSFetcher('https://hnrss.org/frontpage', transformer, storage)),
            ('GitHub Trending', GithubTrendingFetcher(transformer, storage)),
        ]

    async def fetch_all(self) -> List[Article]:
        """
        Fetch from all sources concurrently.
        
        Returns:
            Combined list of all articles
        """
        print("\nStarting fetch from all sources...")
        print(f"   Sources: {len(self.fetchers)}")

        # creating task for all fetchers
        tasks = []
        for name, fetcher in self.fetchers:
            # if isinstance(fetcher,HackerNewsFetcher):
            #     task = fetcher.fetch(limit=30)
            # else:
            #     task = fetcher.fetch()
            task = fetcher.fetch_and_save()
            tasks.append(task)

        # Fetching everything concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine articles
        all_articles = []
        for (name, _), result in zip(self.fetchers, results):
            if isinstance(result,Exception):
                print(f"{name} , failed")
            else:
                print(f'{name}:{len(result)} articles')
                all_articles.extend(result)
        
        # saving combined results
        if all_articles:
            self.storage.save(all_articles,'all_articles.md')

        print(f"\nTotal: {len(all_articles)} articles from {len(self.fetchers)} sources")
        return all_articles

# Testing 
async def main():
    """Testing Orchestrator"""
    orchestrator = FetchOrchestrator()
    articles = await orchestrator.fetch_all()

    print('sample articles')
    for article  in articles[:3]:
        print(f"[{article.source}] {article.title[:50]}.....")


if __name__ =='__main__':
    asyncio.run(main())



