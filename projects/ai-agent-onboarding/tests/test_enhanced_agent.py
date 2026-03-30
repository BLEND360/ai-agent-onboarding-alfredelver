import asyncio
from src.agents.enhanced_filter_agent import EnhancedFilterAgent
import pytest

@pytest.mark.asyncio
async def test_tools():
    """Test agent with tools."""
    agent = EnhancedFilterAgent()

    result = await agent.execute(
        input_path="data/articles/all_articles.md",
        output_path="data/context/enhanced_filtered.md",
    )

    print(f"\nEnhanced filtering complete!")
    print(f"   Check output for tool usage mentions")


if __name__ == "__main__":
    asyncio.run(test_tools())
