"""
PocketFlow-based research agent graph - migrated from LangGraph.

This module replaces the original LangGraph StateGraph with PocketFlow's 
minimalist graph abstraction while maintaining the same research workflow logic.
"""

import os
import json
import yaml
from typing import Dict, Any, List
from datetime import datetime
from pocketflow import Flow, Node
import ollama
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()


class ResearchAgentConfig:
    """Configuration for the research agent - equivalent to original Configuration class."""
    
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.query_generator_model = os.getenv('OLLAMA_QUERY_MODEL', 'phi4')
        self.research_model = os.getenv('OLLAMA_RESEARCH_MODEL', 'deepseek-r1')
        self.reflection_model = os.getenv('OLLAMA_REFLECTION_MODEL', 'llama3.3:70b') 
        self.answer_model = os.getenv('OLLAMA_ANSWER_MODEL', 'deepseek-r1')
        self.max_research_loops = int(os.getenv('MAX_RESEARCH_LOOPS', '2'))
        self.number_of_initial_queries = int(os.getenv('NUMBER_OF_INITIAL_QUERIES', '3'))


class OllamaBaseNode(Node):
    """Base node with Ollama integration - replaces LangGraph node functions."""
    
    def __init__(self, config: ResearchAgentConfig):
        super().__init__()
        self.config = config
        self.client = ollama.Client(host=config.ollama_host)
    
    def get_current_date(self) -> str:
        """Get current date - equivalent to original prompts.get_current_date()."""
        return datetime.now().strftime("%B %d, %Y")
    
    def get_research_topic(self, messages: List[Dict]) -> str:
        """Extract research topic from messages - equivalent to original utils.get_research_topic()."""
        if messages and isinstance(messages[-1], dict):
            return messages[-1].get('content', '')
        return str(messages[-1]) if messages else ''
    
    def call_llm(self, model: str, prompt: str, system: str = None) -> str:
        """Call Ollama LLM - replaces ChatGoogleGenerativeAI calls."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat(model=model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"Error calling LLM {model}: {e}")
            return f"Error: {str(e)}"


class GenerateQueryNode(OllamaBaseNode):
    """Generate search queries - equivalent to original generate_query function."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare query generation - equivalent to original state processing."""
        return {
            'messages': shared.get('messages', []),
            'initial_search_query_count': shared.get('initial_search_query_count', 
                                                   self.config.number_of_initial_queries)
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Generate queries - equivalent to original generate_query logic."""
        messages = prep_res['messages']
        query_count = prep_res['initial_search_query_count']
        
        research_topic = self.get_research_topic(messages)
        current_date = self.get_current_date()
        
        # Adapted from original query_writer_instructions
        prompt = f"""Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {query_count} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL three of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Context: {research_topic}"""

        response = self.call_llm(self.config.query_generator_model, prompt)
        
        try:
            parsed = json.loads(response)
            queries = parsed.get('query', [research_topic])
        except:
            # Fallback
            queries = [research_topic]
        
        return {'query_list': queries}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update state and route - equivalent to continue_to_web_research."""
        shared['query_list'] = exec_res.get('query_list', [])
        shared['initial_search_query_count'] = len(shared['query_list'])
        return 'web_research'


class WebResearchNode(OllamaBaseNode):
    """Web research node - equivalent to original web_research function."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare web research."""
        return {
            'query_list': shared.get('query_list', []),
            'research_topic': self.get_research_topic(shared.get('messages', []))
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web research - equivalent to original web_research with parallel logic."""
        queries = prep_res['query_list']
        research_topic = prep_res['research_topic']
        
        # Process all queries (simulating parallel execution from original Send())
        all_results = []
        all_sources = []
        all_search_queries = []
        
        for idx, search_query in enumerate(queries):
            result = self._single_web_research(search_query, idx)
            if result:
                all_results.extend(result.get('web_research_result', []))
                all_sources.extend(result.get('sources_gathered', []))
                all_search_queries.extend(result.get('search_query', []))
        
        return {
            'web_research_result': all_results,
            'sources_gathered': all_sources,
            'search_query': all_search_queries
        }
    
    def _single_web_research(self, search_query: str, query_id: int) -> Dict[str, Any]:
        """Single web research - equivalent to original WebSearchState processing."""
        current_date = self.get_current_date()
        
        # Adapted from original web_searcher_instructions
        search_prompt = f"""Conduct targeted Google Searches to gather the most recent, credible information on "{search_query}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings.
- Only include the information found in the search results, don't make up any information.

Research Topic: {search_query}"""

        # Perform web search using DuckDuckGo (replacing Google Search API)
        sources_gathered = []
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=5))
                if results:
                    # Compile search results for LLM
                    search_content = "\n\n".join([
                        f"Title: {r['title']}\nURL: {r['href']}\nContent: {r['body']}"
                        for r in results
                    ])
                    
                    # Use LLM to synthesize - equivalent to original genai_client.models.generate_content
                    synthesis_prompt = f"""{search_prompt}

Search Results:
{search_content}

Provide a comprehensive summary of the findings:"""
                    
                    summary = self.call_llm(self.config.research_model, synthesis_prompt)
                    
                    # Create citations - equivalent to original citation system
                    for i, result in enumerate(results):
                        short_url = f'[{query_id}-{i+1}]'
                        sources_gathered.append({
                            'short_url': short_url,
                            'value': result['href'],
                            'title': result['title']
                        })
                        # Insert citation markers like original insert_citation_markers
                        if i < 3:  # Limit citations
                            summary += f" {short_url}"
                    
                    return {
                        'web_research_result': [summary],
                        'sources_gathered': sources_gathered,
                        'search_query': [search_query]
                    }
        
        except Exception as e:
            print(f"Web search error for '{search_query}': {e}")
            return {
                'web_research_result': [f"Search failed for query: {search_query}"],
                'sources_gathered': [],
                'search_query': [search_query]
            }
        
        return {'web_research_result': [], 'sources_gathered': [], 'search_query': []}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update state and route to reflection."""
        # Aggregate results like original LangGraph state reduction
        shared['web_research_result'] = shared.get('web_research_result', []) + exec_res.get('web_research_result', [])
        shared['sources_gathered'] = shared.get('sources_gathered', []) + exec_res.get('sources_gathered', [])
        shared['search_query'] = shared.get('search_query', []) + exec_res.get('search_query', [])
        
        return 'reflection'


class ReflectionNode(OllamaBaseNode):
    """Reflection node - equivalent to original reflection function."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare reflection analysis."""
        return {
            'messages': shared.get('messages', []),
            'web_research_result': shared.get('web_research_result', []),
            'research_loop_count': shared.get('research_loop_count', 0)
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research sufficiency - equivalent to original reflection logic."""
        messages = prep_res['messages']
        summaries = prep_res['web_research_result']
        loop_count = prep_res['research_loop_count']
        
        research_topic = self.get_research_topic(messages)
        current_date = self.get_current_date()
        summaries_text = "\n\n---\n\n".join(summaries)
        
        # Adapted from original reflection_instructions
        prompt = f"""You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Summaries:
{summaries_text}"""

        response = self.call_llm(self.config.reflection_model, prompt)
        
        try:
            parsed = json.loads(response)
            is_sufficient = parsed.get('is_sufficient', True)
            knowledge_gap = parsed.get('knowledge_gap', '')
            follow_up_queries = parsed.get('follow_up_queries', [])
        except:
            # Conservative fallback
            is_sufficient = True
            knowledge_gap = ''
            follow_up_queries = []
        
        return {
            'is_sufficient': is_sufficient,
            'knowledge_gap': knowledge_gap,
            'follow_up_queries': follow_up_queries,
            'research_loop_count': loop_count,
            'number_of_ran_queries': len(prep_res.get('web_research_result', []))
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Route decision - equivalent to original evaluate_research function."""
        # Increment research loop count
        shared['research_loop_count'] = shared.get('research_loop_count', 0) + 1
        
        is_sufficient = exec_res.get('is_sufficient', True)
        follow_up_queries = exec_res.get('follow_up_queries', [])
        
        # Decision logic equivalent to original evaluate_research
        if (is_sufficient or 
            shared['research_loop_count'] >= self.config.max_research_loops or
            not follow_up_queries):
            return 'finalize_answer'
        else:
            # Continue research with follow-up queries
            shared['query_list'] = follow_up_queries
            return 'web_research'


class FinalizeAnswerNode(OllamaBaseNode):
    """Finalize answer - equivalent to original finalize_answer function."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare final answer generation."""
        return {
            'messages': shared.get('messages', []),
            'web_research_result': shared.get('web_research_result', []),
            'sources_gathered': shared.get('sources_gathered', [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final answer - equivalent to original finalize_answer logic."""
        messages = prep_res['messages']
        summaries = prep_res['web_research_result']
        sources_gathered = prep_res['sources_gathered']
        
        research_topic = self.get_research_topic(messages)
        current_date = self.get_current_date()
        summaries_text = "\n---\n\n".join(summaries)
        
        # Adapted from original answer_instructions
        prompt = f"""Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step.
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- you MUST include all the citations from the summaries in the answer correctly.

User Context:
- {research_topic}

Summaries:
{summaries_text}"""

        final_answer = self.call_llm(self.config.answer_model, prompt)
        
        # Replace short URLs with actual URLs - equivalent to original citation replacement
        cited_sources = []
        for source in sources_gathered:
            if source['short_url'] in final_answer:
                final_answer = final_answer.replace(source['short_url'], source['value'])
                cited_sources.append(source)
        
        return {
            'final_answer': final_answer,
            'cited_sources': cited_sources,
            'all_sources': sources_gathered  # Include all collected sources
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update final state - equivalent to original state update."""
        shared['messages'].append({
            'role': 'assistant', 
            'content': exec_res.get('final_answer', '')
        })
        # Keep both cited sources (used in answer) and all sources (collected during research)
        shared['sources_gathered'] = exec_res.get('cited_sources', [])
        shared['all_sources_collected'] = exec_res.get('all_sources', [])
        return 'END'


def create_research_graph() -> Flow:
    """Create research agent graph - equivalent to original StateGraph builder."""
    
    # Initialize configuration
    config = ResearchAgentConfig()
    
    # Create nodes - equivalent to original builder.add_node calls
    generate_query = GenerateQueryNode(config)
    web_research = WebResearchNode(config)
    reflection = ReflectionNode(config)
    finalize_answer = FinalizeAnswerNode(config)
    
    # Create flow - equivalent to original StateGraph
    flow = Flow()
    
    # Build graph structure - equivalent to original edges and conditional edges
    flow.start(generate_query)
    
    # Route connections - equivalent to original add_edge and add_conditional_edges
    generate_query - "web_research" >> web_research
    web_research - "reflection" >> reflection
    reflection - "web_research" >> web_research      # Continue research loop
    reflection - "finalize_answer" >> finalize_answer # Generate final answer
    
    return flow


def run_research_graph(question: str) -> Dict[str, Any]:
    """Run research graph - equivalent to original graph.invoke()."""
    
    # Initialize state - equivalent to original OverallState
    shared = {
        'messages': [{'role': 'user', 'content': question}],
        'query_list': [],
        'web_research_result': [],
        'sources_gathered': [],
        'search_query': [],
        'research_loop_count': 0,
        'initial_search_query_count': None
    }
    
    # Create and run graph
    graph = create_research_graph()
    result = graph.run(shared)
    
    # Return structured result - equivalent to original graph output
    return {
        'messages': shared.get('messages', []),
        'sources_gathered': shared.get('sources_gathered', []),  # Only cited sources
        'all_sources_collected': shared.get('all_sources_collected', []),  # All collected sources
        'web_research_result': shared.get('web_research_result', []),
        'research_loop_count': shared.get('research_loop_count', 0),
        'query_list': shared.get('query_list', [])
    }


# Maintain compatibility with original graph interface
graph = create_research_graph()