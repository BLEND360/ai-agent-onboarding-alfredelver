import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.summarizer_agent import SummarizerAgent


@pytest.mark.asyncio
@patch.object(
    SummarizerAgent,
    "_call_llm",
    new_callable=AsyncMock,
    return_value="AI continues to advance rapidly with new LLM releases and research breakthroughs.",
)
async def test(mock_llm):
    agent = SummarizerAgent()
    await agent.execute(
        input_path="data/context/filtered_articles.md",
        output_path="data/context/summary.md",
    )
    assert mock_llm.called


if __name__ == "__main__":
    asyncio.run(test())
