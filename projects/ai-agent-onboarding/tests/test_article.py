from datetime import datetime

import pytest

from src.models.articles import Article


def test_article_creation():
    article = Article(
        title="tst", url="https://test.com", published_at=datetime.now(), source="test"
    )
    assert article.title == "tst"
    assert article.url == "https://test.com"


def test_article_validation():
    """Test article validation."""
    with pytest.raises(ValueError):
        Article(
            title="",  # Empty title should fail
            url="https://test.com",
            published_at=datetime.now(),
            source="test",
        )


def test_article_to_markdown():
    "testing markdown conversion"
    article = Article(
        title="Test Article",
        url="https://test.com",
        published_at=datetime.now(),
        source="test",
        summary="Test summary",
    )

    md = article.to_markdown()
    assert "Test Article" in md
    assert "https://test.com" in md
    assert "test" in md
