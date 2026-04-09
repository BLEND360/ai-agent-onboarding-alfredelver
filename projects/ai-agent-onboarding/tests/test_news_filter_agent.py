import json
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.news_filter_agent import NewsFilterAgent
from pathlib import Path
import tempfile


async def _fake_llm(prompt):
    """Return deterministic JSON based on article title in the prompt."""
    if "GPT-4" in prompt:
        return json.dumps(
            {
                "relevant": True,
                "relevance_score": 10,
                "reasoning": "Major LLM release",
                "key_topics": ["LLM", "GPT"],
            }
        )
    else:
        return json.dumps(
            {
                "relevant": False,
                "relevance_score": 1,
                "reasoning": "Web dev, not AI",
                "key_topics": [],
            }
        )


@pytest.mark.asyncio
@patch.object(NewsFilterAgent, "_call_llm", side_effect=_fake_llm)
async def test_agent_filters_articles(mock_llm):
    """Test agent filters correctly."""
    # Create temp input file
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "input.md"
        output_file = Path(tmpdir) / "output.md"

        # Write test articles
        input_file.write_text("""
## GPT-4 Released by OpenAI

**URL:** https://example.com/gpt4

OpenAI announces GPT-4 with enhanced capabilities.

---

## New JavaScript Framework

**URL:** https://example.com/js

React alternative for web development.
""")

        # Run agent
        agent = NewsFilterAgent()
        result = await agent.execute(str(input_file), str(output_file))

        # Check output
        assert output_file.exists()
        content = output_file.read_text()

        # Should include GPT-4
        assert "GPT-4" in content

        # Should not include JS framework
        assert "JavaScript" not in content


@pytest.mark.asyncio
async def test_tool_usage():
    """Test tools are callable."""
    from src.tools.calculator import calculator
    from src.tools.websearch import web_search

    # Test calculator
    result = calculator("2 + 2")
    assert result["success"]
    assert result["result"] == 4

    # Test search
    result = web_search("AI news")
    assert result["success"]
    assert len(result["results"]) > 0
