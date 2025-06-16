# PocketFlow Research Agent Backend

A lightweight, self-hosted research agent built with PocketFlow and Ollama, migrated from the original LangGraph implementation.

## Key Benefits

- **95% Simpler**: 100-line PocketFlow core vs 37K-line LangGraph
- **Zero Vendor Lock-in**: Use any Ollama-compatible models
- **Cost Effective**: No API fees, run locally or on your infrastructure
- **Privacy Focused**: All data stays within your control
- **Easy Development**: Simplified codebase and dependencies

## Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Ollama configuration
```

### 2. Ollama Setup
```bash
# Install required models
ollama pull phi4              # Query generation
ollama pull deepseek-r1       # Research & synthesis  
ollama pull llama3.3:70b      # Reflection analysis

# Verify models are available
ollama list
```

### 3. Validation
```bash
# Validate your setup
python validate_setup.py

# Test the research agent
python test_new_graph.py
```

### 4. Start Development Server
```bash
# Start FastAPI server
python run_server.py

# Server will be available at:
# - API: http://localhost:8000
# - Health: http://localhost:8000/api/health  
# - Frontend: http://localhost:8000/app (if built)
```

## Environment Configuration

Edit `.env` file:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_QUERY_MODEL=phi4
OLLAMA_RESEARCH_MODEL=deepseek-r1
OLLAMA_REFLECTION_MODEL=llama3.3:70b
OLLAMA_ANSWER_MODEL=deepseek-r1

# Research Configuration  
MAX_RESEARCH_LOOPS=2
NUMBER_OF_INITIAL_QUERIES=3
```

### Remote Ollama Setup
If using remote Ollama, update `OLLAMA_HOST`:
```bash
OLLAMA_HOST=http://your-ollama-server:11434
```

See `ollama-setup.md` for detailed remote configuration.

## Architecture

### Core Workflow
```
User Question 
    ↓
GenerateQueryNode (phi4)
    ↓  
WebResearchNode (deepseek-r1) - Web search + synthesis
    ↓
ReflectionNode (llama3.3:70b) - Analyze sufficiency
    ↓
[Continue Research] OR [FinalizeAnswerNode (deepseek-r1)]
    ↓
Final Answer with Citations
```

### File Structure
```
backend-new/
├── src/
│   ├── graph.py          # Main PocketFlow workflow (recommended)
│   ├── nodes.py          # Prototype nodes implementation  
│   ├── flow.py           # Prototype flow implementation
│   └── app.py            # FastAPI server
├── test_new_graph.py     # End-to-end testing
├── test_agent.py         # Prototype testing
├── test_flow_mock.py     # Mock testing (no LLM)
├── validate_setup.py     # Setup validation
├── run_server.py         # Development server
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
└── ollama-setup.md       # Ollama configuration guide
```

## API Usage

### Research Endpoint
```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest developments in quantum computing?",
    "context": "Focus on 2024 developments"
  }'
```

### Response Format
```json
{
  "question": "What are the latest developments in quantum computing?",
  "answer": "Comprehensive answer with citations...",
  "sources": ["url1", "url2"],
  "research_summary": {
    "queries_used": 3,
    "research_loops": 1,
    "reflection": {...}
  }
}
```

## Testing

### Available Tests
```bash
# Mock testing (no LLM required)
python test_flow_mock.py

# End-to-end testing with Ollama
python test_new_graph.py

# Prototype testing  
python test_agent.py

# Setup validation
python validate_setup.py
```

### Test Output
Tests show:
- Research loop count (depth of investigation)
- Cited sources (used in answer) vs All collected sources
- Answer quality and citation accuracy

## Development

### Adding New Features
1. Use `graph.py` for production code
2. Use `nodes.py`/`flow.py` for prototyping
3. Inherit from `OllamaBaseNode` for LLM integration
4. Follow shared state patterns

### Node Development Pattern
```python
class CustomNode(OllamaBaseNode):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare data for processing
        return {...}
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        # Main processing logic
        result = self.call_llm(model, prompt, system)
        return {...}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        # Update shared state and return next node
        shared['data'] = exec_res
        return 'next_node'
```

### Graph Development
```python
# Create flow with conditional routing
flow = Flow()
flow.start(start_node)
node1 - "condition" >> node2
node2 - "continue" >> node1
node2 - "finish" >> end_node
```

## Troubleshooting

### Common Issues

**Import Errors**
- Run `python validate_setup.py` to check setup
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Ollama Connection Errors**  
- Check `OLLAMA_HOST` in `.env`
- Verify Ollama server is running
- Test with: `ollama list`

**Model Not Found**
- Pull required models: `ollama pull model-name`
- Check model names in `.env` match available models

**Empty Responses**
- Check Ollama server logs
- Verify model compatibility
- Try with mock tests first

### Debug Mode
Set environment variables for detailed logging:
```bash
export PYTHONPATH=./src
export DEBUG=1
python test_new_graph.py
```

## Performance

### Resource Requirements
- **Memory**: 8GB+ RAM for 7B models, 16GB+ for 13B models
- **Storage**: 5-20GB per model depending on size
- **CPU/GPU**: GPU recommended for larger models

### Model Selection
- **Development**: Use smaller models (phi4, smaller variants)
- **Production**: Use full-size models for best quality
- **Resource-Constrained**: Consider quantized models

## Migration from LangGraph

This backend provides the same research capabilities as the original LangGraph implementation with:
- ✅ Same research quality
- ✅ Improved research depth (configurable loops)
- ✅ Better citation management (cited vs collected sources)
- ✅ Simplified development and deployment
- ❌ No real-time streaming (uses standard HTTP)

See `../migration-summary.md` for detailed comparison.

## Contributing

1. Follow the established patterns in `graph.py`
2. Add tests for new functionality
3. Update documentation as needed
4. Validate changes with `python validate_setup.py`