import asyncio
from src.database.db_manager import DatabaseManager
from pathlib import Path
import re
from datetime import datetime


async def populate_from_markdown():
    """Populate database from markdown files."""
    db = DatabaseManager()
    await db.initialize()

    articles_dir = Path("data/articles")

    for md_file in articles_dir.glob("*.md"):
        print(f"Reading {md_file.name}...")
        content = md_file.read_text()

        sections = content.split('---')

        for section in sections:
            if '##' not in section:
                continue

            title_match = re.search(r'## (.+)', section)
            if not title_match:
                continue
            title = title_match.group(1).strip()

            url_match = re.search(r'\*\*URL:\*\* (.+)', section)
            if not url_match:
                continue
            url = url_match.group(1).strip()

            source_match = re.search(r'\*\*Source:\*\* (.+)', section)
            source = source_match.group(1).strip() if source_match else 'unknown'

            lines = [
                line for line in section.split('\n')
                if line.strip() and not line.startswith('**')
            ]
            summary = lines[-1] if lines else ""

            await db.insert_article({
                'title': title,
                'url': url,
                'source': source,
                'published_at': datetime.now().isoformat(),
                'summary': summary,
            })

    articles = await db.query_articles(limit=1000)
    print(f"\nDatabase populated with {len(articles)} articles")


if __name__ == "__main__":
    asyncio.run(populate_from_markdown())