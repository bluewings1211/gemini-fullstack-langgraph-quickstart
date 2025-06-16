"""PocketFlow nodes for research agent workflow."""

import json
import yaml
from typing import Dict, Any, List
from pocketflow import Node
import ollama
from duckduckgo_search import DDGS
import os
from dotenv import load_dotenv

load_dotenv()


class OllamaNode(Node):
    """Base node for Ollama LLM interactions."""
    
    def __init__(self, model_name: str = None):
        super().__init__()
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.client = ollama.Client(host=self.ollama_host)
        self.model_name = model_name
    
    def call_llm(self, prompt: str, system: str = None) -> str:
        """Call Ollama LLM with prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error: {str(e)}"


class QueryGenerationNode(OllamaNode):
    """Generate search queries from user input."""
    
    def __init__(self):
        query_model = os.getenv('OLLAMA_QUERY_MODEL', 'phi4')
        super().__init__(query_model)
        self.max_queries = int(os.getenv('NUMBER_OF_INITIAL_QUERIES', '3'))
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for query generation."""
        return {
            'question': shared.get('question', ''),
            'context': shared.get('context', '')
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Generate search queries."""
        question = prep_res['question']
        context = prep_res.get('context', '')
        
        system_prompt = """You are a research assistant that generates effective search queries.
Your task is to create 1-3 optimized search queries that will help gather comprehensive information to answer the user's question.

Output your response in YAML format:
queries:
  - query: "search query 1"
    rationale: "why this query is useful"
  - query: "search query 2" 
    rationale: "why this query is useful"
"""
        
        user_prompt = f"""Question: {question}

{f"Additional context: {context}" if context else ""}

Generate {self.max_queries} search queries to research this question thoroughly."""

        response = self.call_llm(user_prompt, system_prompt)
        
        try:
            # Parse YAML response
            parsed = yaml.safe_load(response)
            queries = [item['query'] for item in parsed.get('queries', [])]
            return {'queries': queries}
        except:
            # Fallback - extract queries from text
            return {'queries': [question]}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update shared state with generated queries."""
        shared['search_queries'] = exec_res.get('queries', [])
        return 'web_research'


class WebResearchNode(OllamaNode):
    """Perform web research for given queries."""
    
    def __init__(self):
        research_model = os.getenv('OLLAMA_RESEARCH_MODEL', 'deepseek-r1')
        super().__init__(research_model)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for web research."""
        return {
            'queries': shared.get('search_queries', []),
            'question': shared.get('question', '')
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web searches and summarize results."""
        queries = prep_res['queries']
        question = prep_res['question']
        research_results = []
        
        # Perform web searches
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = list(ddgs.text(query, max_results=5))
                    if results:
                        # Summarize search results using LLM
                        search_content = "\n\n".join([
                            f"Title: {r['title']}\nURL: {r['href']}\nContent: {r['body']}"
                            for r in results
                        ])
                        
                        system_prompt = """You are a research assistant. Summarize the search results to extract information relevant to answering the research question. Focus on key facts, findings, and insights."""
                        
                        user_prompt = f"""Research Question: {question}
Search Query: {query}

Search Results:
{search_content}

Provide a concise summary of the relevant information found:"""
                        
                        summary = self.call_llm(user_prompt, system_prompt)
                        
                        research_results.append({
                            'query': query,
                            'summary': summary,
                            'sources': [r['href'] for r in results]
                        })
                except Exception as e:
                    print(f"Error searching for '{query}': {e}")
                    continue
        
        return {'research_results': research_results}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update shared state with research results."""
        if 'research_results' not in shared:
            shared['research_results'] = []
        
        shared['research_results'].extend(exec_res.get('research_results', []))
        return 'reflection'


class ReflectionNode(OllamaNode):
    """Analyze research results and decide next action."""
    
    def __init__(self):
        reflection_model = os.getenv('OLLAMA_REFLECTION_MODEL', 'llama3.3:70b')
        super().__init__(reflection_model)
        self.max_loops = int(os.getenv('MAX_RESEARCH_LOOPS', '2'))
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for reflection."""
        return {
            'question': shared.get('question', ''),
            'research_results': shared.get('research_results', []),
            'research_loop_count': shared.get('research_loop_count', 0)
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research sufficiency and decide next action."""
        question = prep_res['question']
        research_results = prep_res['research_results']
        loop_count = prep_res['research_loop_count']
        
        # Compile research summary
        research_summary = "\n\n".join([
            f"Query: {r['query']}\nFindings: {r['summary']}"
            for r in research_results
        ])
        
        system_prompt = """You are a critical research analyst with high standards for comprehensive analysis. Your job is to identify knowledge gaps and push for deeper research.

IMPORTANT: Be very strict about what constitutes "sufficient" research. Only mark as sufficient if you have:
1. Multiple perspectives from different authoritative sources
2. Quantitative data and specific examples
3. Analysis of both direct and indirect impacts
4. Recent/current information (within 6-12 months)
5. Comprehensive coverage of all major aspects of the question

Bias toward finding knowledge gaps and requesting additional research.

Output your response in YAML format:
analysis:
  sufficient: true/false
  reasoning: "detailed explanation of what's missing or why more research is needed"
  knowledge_gaps: ["specific gap 1", "specific gap 2"] # always provide if not sufficient
  follow_up_queries: ["targeted query 1", "targeted query 2"] # always provide if not sufficient
"""
        
        user_prompt = f"""Research Question: {question}

Current Research Findings:
{research_summary}

Research Loop Count: {loop_count}/{self.max_loops}

CRITICAL ANALYSIS REQUIRED:
1. Are there missing quantitative data points (specific numbers, percentages, financial figures)?
2. Do we need more recent market data or expert opinions?
3. Are there different stakeholder perspectives missing?
4. What about competitive analysis or alternative scenarios?
5. Are there regulatory, technical, or economic factors not yet explored?

Be very critical - most research can be improved with additional targeted queries."""

        response = self.call_llm(user_prompt, system_prompt)
        
        try:
            parsed = yaml.safe_load(response)
            analysis = parsed.get('analysis', {})
            
            # Force finalization if max loops reached
            if loop_count >= self.max_loops:
                analysis['sufficient'] = True
                analysis['reasoning'] = f"Maximum research loops ({self.max_loops}) reached."
            
            return analysis
        except:
            # Fallback - be conservative and continue research if not at max loops
            if loop_count < self.max_loops:
                return {
                    'sufficient': False,
                    'reasoning': 'Error parsing analysis, continuing research for safety.',
                    'knowledge_gaps': ['Analysis parsing error - need more specific data'],
                    'follow_up_queries': [f'{question} latest data 2024', f'{question} expert analysis']
                }
            else:
                return {
                    'sufficient': True,
                    'reasoning': 'Max loops reached, proceeding to answer.'
                }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Decide next action based on analysis."""
        shared['reflection_result'] = exec_res
        
        if exec_res.get('sufficient', True):
            return 'finalize_answer'
        else:
            # Continue research with follow-up queries
            follow_up_queries = exec_res.get('follow_up_queries', [])
            if follow_up_queries:
                shared['search_queries'] = follow_up_queries
                shared['research_loop_count'] = shared.get('research_loop_count', 0) + 1
                return 'web_research'
            else:
                return 'finalize_answer'


class FinalizeAnswerNode(OllamaNode):
    """Generate final answer with citations."""
    
    def __init__(self):
        answer_model = os.getenv('OLLAMA_ANSWER_MODEL', 'deepseek-r1')
        super().__init__(answer_model)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for answer generation."""
        return {
            'question': shared.get('question', ''),
            'research_results': shared.get('research_results', []),
            'reflection_result': shared.get('reflection_result', {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive answer with citations."""
        question = prep_res['question']
        research_results = prep_res['research_results']
        
        # Compile research with sources
        research_with_sources = []
        all_sources = []
        
        for i, result in enumerate(research_results):
            research_with_sources.append(f"Research {i+1}: {result['summary']}")
            all_sources.extend(result['sources'])
        
        research_content = "\n\n".join(research_with_sources)
        
        system_prompt = """You are a research assistant providing comprehensive answers with citations.

Guidelines:
1. Provide a well-structured, informative answer
2. Include relevant citations in [1], [2] format
3. Be objective and acknowledge limitations
4. Synthesize information from multiple sources
"""
        
        user_prompt = f"""Question: {question}

Research Findings:
{research_content}

Available Sources:
{chr(10).join([f"[{i+1}] {url}" for i, url in enumerate(set(all_sources))])}

Provide a comprehensive answer to the question using the research findings. Include appropriate citations."""

        answer = self.call_llm(user_prompt, system_prompt)
        
        return {
            'answer': answer,
            'sources': list(set(all_sources))
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update shared state with final answer."""
        shared['final_answer'] = exec_res.get('answer', '')
        shared['sources'] = exec_res.get('sources', [])
        return 'complete'