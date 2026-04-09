import asyncio
import pytest
from pathlib import Path
from src.agents.summarizer_agent import SummarizerAgent


@pytest.mark.asyncio
async def test():
    # Rate limit: space out from prior API calls
    await asyncio.sleep(13)

    agent = SummarizerAgent()
    await agent.execute(
        input_path="data/context/filtered_articles.md",
        output_path="data/context/summary.md",
    )

    # Verify output was created
    assert Path("data/context/summary.md").exists()


if __name__ == "__main__":
    asyncio.run(test())
