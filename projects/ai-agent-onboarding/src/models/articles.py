from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """represents a class for news articles
    Using dataclass for automatic __init__, __repr__, etc.
    """

    title: str
    url: str
    published_at: datetime
    source: str
    summary: str = ""
    score: int = 0

    def __post_init__(self):
        "Validate after initialization"
        if not self.title:
            raise ValueError("The article should have a title")
        if not self.url:
            raise ValueError("The article should have a url")

    def to_markdown(self) -> str:
        """Convert the article text to markdown"""
        return f"""## {self.title}

                **Source:**{self.source}
                **URL:** {self.url}  
                **Published:** {self.published_at.strftime('%Y-%m-%d %H:%M')}  
                **Score:** {self.score}

                {self.summary}

                """


# Quick testing
if __name__ == "__main__":
    article = Article(
        title="test article",
        url="https://example.com",
        published_at=datetime.now(),
        source="test",
        summary="test summary",
    )
    print(article.to_markdown())
    print("Success")
