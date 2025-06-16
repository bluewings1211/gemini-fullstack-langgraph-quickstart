"""PocketFlow workflow for research agent."""

from pocketflow import Flow
try:
    from .nodes import (
        QueryGenerationNode,
        WebResearchNode, 
        ReflectionNode,
        FinalizeAnswerNode
    )
except ImportError:
    from nodes import (
        QueryGenerationNode,
        WebResearchNode, 
        ReflectionNode,
        FinalizeAnswerNode
    )


def create_research_flow() -> Flow:
    """Create the research agent workflow using PocketFlow."""
    
    # Initialize nodes
    query_gen = QueryGenerationNode()
    web_research = WebResearchNode()
    reflection = ReflectionNode()
    finalize = FinalizeAnswerNode()
    
    # Create and configure flow
    flow = Flow()
    
    # Start with query generation
    flow.start(query_gen)
    
    # Connect nodes with routing
    query_gen - "web_research" >> web_research
    web_research - "reflection" >> reflection
    
    # Reflection can either continue research or finalize
    reflection - "web_research" >> web_research  # Continue research loop
    reflection - "finalize_answer" >> finalize   # Generate final answer
    
    return flow


def run_research_agent(question: str, context: str = "") -> dict:
    """Run the research agent workflow."""
    
    # Create shared state
    shared = {
        'question': question,
        'context': context,
        'research_loop_count': 0,
        'research_results': [],
        'search_queries': [],
        'reflection_result': {},
        'final_answer': '',
        'sources': []
    }
    
    # Create and run flow
    flow = create_research_flow()
    result = flow.run(shared)
    
    # Return structured response
    return {
        'question': question,
        'answer': shared.get('final_answer', 'No answer generated'),
        'sources': shared.get('sources', []),
        'research_summary': {
            'queries_used': len(shared.get('research_results', [])),
            'research_loops': shared.get('research_loop_count', 0),
            'reflection': shared.get('reflection_result', {})
        }
    }