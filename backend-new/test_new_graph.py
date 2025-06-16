"""Test script for new PocketFlow research graph."""

import sys
from pathlib import Path

# Add src to path  
sys.path.append(str(Path(__file__).parent / "src"))

def test_new_graph():
    """Test the new PocketFlow research graph."""
    
    print("🔬 Testing New PocketFlow Research Graph")
    print("=" * 60)
    
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
    print("\n🔍 Starting research with new graph...")
    
    try:
        from graph import run_research_graph
        
        result = run_research_graph(question)
        
        print("\n✅ Research completed with new graph!")
        
        # Extract answer from messages
        messages = result.get('messages', [])
        answer = ""
        if messages and len(messages) > 1:
            answer = messages[-1].get('content', 'No answer found')
        
        print(f"Answer: {answer[:200]}..." if len(answer) > 200 else f"Answer: {answer}")
        
        # Show cited sources (used in answer)
        cited_sources = result.get('sources_gathered', [])
        print(f"\n📚 Cited Sources ({len(cited_sources)}):")
        for i, source in enumerate(cited_sources, 1):
            if isinstance(source, dict):
                title = source.get('title', 'Unknown')
                url = source.get('value', source.get('short_url', 'Unknown'))
                print(f"  [{i}] {title} - {url}")
            else:
                print(f"  [{i}] {source}")
        
        # Show all collected sources
        all_sources = result.get('all_sources_collected', [])
        if all_sources and len(all_sources) > len(cited_sources):
            print(f"\n📖 All Collected Sources ({len(all_sources)}):")
            for i, source in enumerate(all_sources, 1):
                if isinstance(source, dict):
                    title = source.get('title', 'Unknown')
                    url = source.get('value', source.get('short_url', 'Unknown'))
                    print(f"  [{i}] {title} - {url}")
                else:
                    print(f"  [{i}] {source}")
        
        # Show research summary
        print(f"\n📊 Research Summary:")
        print(f"  - Research loops: {result.get('research_loop_count', 0)}")
        print(f"  - Queries executed: {len(result.get('web_research_result', []))}")
        print(f"  - Total queries generated: {len(result.get('query_list', []))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_original():
    """Compare structure with original flow."""
    print("\n🔄 Comparing with Original Flow Structure")
    print("=" * 50)
    
    try:
        from graph import ResearchAgentConfig, create_research_graph
        from flow import create_research_flow
        
        # Test config
        config = ResearchAgentConfig()
        print(f"✅ New config loaded:")
        print(f"  - Query model: {config.query_generator_model}")
        print(f"  - Research model: {config.research_model}")
        print(f"  - Reflection model: {config.reflection_model}")
        print(f"  - Answer model: {config.answer_model}")
        print(f"  - Max loops: {config.max_research_loops}")
        
        # Test graph creation
        new_graph = create_research_graph()
        old_flow = create_research_flow()
        
        print(f"\n✅ Both graphs created successfully")
        print(f"  - New PocketFlow graph: {type(new_graph).__name__}")
        print(f"  - Original flow: {type(old_flow).__name__}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing PocketFlow Migration")
    print("=" * 60)
    
    # Test comparison first
    comparison_success = compare_with_original()
    
    if comparison_success:
        # Test actual execution
        test_success = test_new_graph()
        
        if test_success:
            print("\n🎉 All tests passed! Migration successful.")
            print("\nNext steps:")
            print("1. Test with various question types")
            print("2. Compare response quality with original")
            print("3. Performance benchmarking")
        else:
            print("\n💥 Execution test failed.")
    else:
        print("\n💥 Structure comparison failed.")
    
    sys.exit(0 if (comparison_success and test_success if comparison_success else False) else 1)