"""Test script for PocketFlow research agent."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from flow import run_research_agent

def test_research_agent():
    """Test the research agent with a sample question."""
    
    print("🔬 Testing PocketFlow Research Agent")
    print("=" * 50)
    
    # Test question
    #question = "What are the latest developments in quantum computing in 2024?"
    #question = "川普推動的關稅政策是否為美元走弱的主因?"
    #question = "AI 能力增強以及 AI tool 的普及對房地產價格是推升嗎?"
    question = "冥想與自省能提高收入能力?"
    #question = "如何利用量子領域中的張量網路知識來壓縮大型語言模型?"
    #question = "台灣新竹縣市人口成長與周邊房價的關係是?"
    #question = "CompactifAI 近期有論文提到量子張量網路概念可以應用在模型壓縮上，有其他公司有類似的壓縮方式可以達到 30%以上的壓縮嗎?"
    #question = "LLM壓縮方式的演進讓大模型能在更小硬體spec的機器上部署，這對於Nvidia 的股價影響是？"
    
    print(f"Question: {question}")
    print("\n🔍 Starting research...")
    
    try:
        result = run_research_agent(question)
        
        print("\n✅ Research completed!")
        print(f"Answer: {result['answer']}")
        print(f"\n📚 Sources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'][:5], 1):  # Show first 5 sources
            print(f"  [{i}] {source}")
        
        print(f"\n📊 Research Summary:")
        summary = result['research_summary']
        print(f"  - Queries used: {summary['queries_used']}")
        print(f"  - Research loops: {summary['research_loops']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_research_agent()
    sys.exit(0 if success else 1)
