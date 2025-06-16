# AI Research Agent: LangGraph & PocketFlow Implementations

This project demonstrates advanced AI research agents using two different architectures:
- **Original**: LangGraph + Google Gemini (real-time streaming)
- **New**: PocketFlow + Ollama (lightweight, self-hosted)

Both implementations provide comprehensive research capabilities with dynamic query generation, web research, iterative refinement, and citation-backed answers.

![Research Agent Flow](./agent.png)

## 🌟 Choose Your Implementation

### 🚀 **Recommended: PocketFlow + Ollama** (`backend-new/`)
- **95% Simpler**: 100-line core vs 37K-line dependency
- **Zero Cost**: No API fees, runs locally/remote
- **Privacy First**: All data stays under your control
- **Zero Vendor Lock-in**: Use any Ollama-compatible models
- **Easy Development**: Minimal dependencies and complexity

### 🔬 **Reference: LangGraph + Gemini** (`backend/`)
- **Production-Proven**: Mature LangGraph ecosystem
- **Real-time Streaming**: Live research progress updates
- **Cloud-Ready**: Integrated with LangSmith and Google APIs
- **Enterprise Features**: Advanced monitoring and deployment

## Quick Start

### Option A: PocketFlow Backend (Recommended)

```bash
# 1. Setup environment
cd backend-new
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Ollama
cp .env.example .env
# Edit .env with your Ollama settings

# 3. Install models
ollama pull phi4              # Query generation
ollama pull deepseek-r1       # Research & synthesis
ollama pull llama3.3:70b      # Reflection analysis

# 4. Validate and test
python validate_setup.py
python test_new_graph.py

# 5. Start server
python run_server.py
# Visit: http://localhost:8000
```

### Option B: LangGraph Backend (Legacy)

```bash
# 1. Setup environment
cd backend
pip install .

# 2. Configure Google Gemini
cp .env.example .env
# Add your GEMINI_API_KEY

# 3. Start server
langgraph dev
# Visit: http://localhost:2024
```

### Frontend (Both Backends)

```bash
cd frontend
npm install
npm run dev
# Visit: http://localhost:5173
```

## Architecture Comparison

### PocketFlow Implementation
```
User Question → GenerateQueryNode → WebResearchNode → ReflectionNode → FinalizeAnswerNode
                     (phi4)           (deepseek-r1)      (llama3.3)      (deepseek-r1)
```

**Key Features:**
- Simple dictionary-based state management
- Configurable research depth (1-3+ loops)
- Dual citation system (cited vs collected sources)
- Standard REST API communication

### LangGraph Implementation  
```
User Question → generate_query → web_research → reflection → finalize_answer
                   (Gemini)        (Gemini)      (Gemini)      (Gemini)
```

**Key Features:**
- TypedDict-based state with reducers
- Real-time streaming with progress updates
- Google Search API integration
- WebSocket communication

## Project Structure

```
├── frontend/                 # React application (shared)
├── backend/                  # LangGraph + Gemini (legacy)
├── backend-new/              # PocketFlow + Ollama (recommended)
│   ├── src/
│   │   ├── graph.py          # Main workflow
│   │   ├── nodes.py          # Prototype implementation
│   │   └── app.py            # FastAPI server
│   ├── test_new_graph.py     # End-to-end testing
│   ├── validate_setup.py     # Setup validation
│   └── run_server.py         # Development server
├── CLAUDE.md                 # Development guide
└── migration-summary.md      # Migration details
```

## Configuration

### PocketFlow Backend (.env)
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_QUERY_MODEL=phi4
OLLAMA_RESEARCH_MODEL=deepseek-r1
OLLAMA_REFLECTION_MODEL=llama3.3:70b
OLLAMA_ANSWER_MODEL=deepseek-r1

# Research Settings
MAX_RESEARCH_LOOPS=2
NUMBER_OF_INITIAL_QUERIES=3
```

### LangGraph Backend (.env)
```bash
GEMINI_API_KEY=your-google-gemini-api-key
LANGSMITH_API_KEY=your-langsmith-key  # optional
```

## How the Research Process Works

Both implementations follow the same core research methodology:

1. **Query Generation**: Analyze user question and generate 1-3 optimized search queries
2. **Web Research**: Perform parallel web searches and synthesize findings
3. **Reflection**: Analyze research sufficiency and identify knowledge gaps
4. **Iterative Refinement**: Generate follow-up queries if needed (up to max loops)
5. **Answer Synthesis**: Create comprehensive answer with proper citations

### Research Loop Example
```
Question: "What are the latest quantum computing developments in 2024?"

Loop 1: ["quantum computing 2024", "quantum breakthroughs 2024"]
→ Reflection: Need more specific company/technical details
Loop 2: ["IBM quantum roadmap 2024", "Google quantum chip 2024"]  
→ Reflection: Sufficient information gathered
Final: Comprehensive answer with 15+ citations
```

## API Usage

### PocketFlow API
```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Latest AI developments in 2024",
    "context": "Focus on breakthrough models"
  }'
```

### LangGraph API
```bash
# Streaming endpoint (requires LangGraph SDK)
POST http://localhost:2024/threads/{thread_id}/runs
```

## Testing & Development

### PocketFlow Testing
```bash
cd backend-new

# Validate setup
python validate_setup.py

# Mock testing (no LLM)
python test_flow_mock.py

# Full testing
python test_new_graph.py

# Prototype testing
python test_agent.py
```

### LangGraph Testing
```bash
cd backend

# Unit tests
make test

# Development server
langgraph dev
```

## Performance & Resources

### PocketFlow Requirements
- **RAM**: 8GB+ (7B models), 16GB+ (13B models)
- **Storage**: 5-20GB per model
- **Network**: DuckDuckGo API access
- **Cost**: Free (local models)

### LangGraph Requirements
- **API Keys**: Google Gemini API
- **Network**: Google Search API access
- **Infrastructure**: Redis + Postgres (production)
- **Cost**: Pay-per-API-call

## Migration Guide

### From LangGraph to PocketFlow
1. Review `migration-summary.md` for detailed comparison
2. Set up Ollama with recommended models
3. Test functionality with `backend-new/test_new_graph.py`
4. Update frontend API endpoints if needed

### Key Differences
| Feature | LangGraph | PocketFlow |
|---------|-----------|------------|
| **Complexity** | 37K+ lines | 100 lines core |
| **Dependencies** | 20+ packages | 8 packages |
| **Streaming** | ✅ Real-time | ❌ Standard HTTP |
| **Cost** | 💰 API fees | 🆓 Free |
| **Privacy** | ☁️ Cloud | 🔒 Local |
| **Setup** | Complex | Simple |

## Technologies Used

### Core Technologies
- **Frontend**: React + Vite + TailwindCSS + Shadcn/ui
- **Search**: DuckDuckGo Search API
- **Citation**: Automatic URL processing and citation management

### Backend Options
- **PocketFlow**: Minimalist workflow framework + Ollama models
- **LangGraph**: Advanced graph framework + Google Gemini models

## Development

### Starting New Features
1. **Use PocketFlow** (`backend-new/`) for new development
2. Follow patterns in `backend-new/src/graph.py`
3. Test with validation scripts
4. See `CLAUDE.md` for detailed development guidance

### Contributing
1. Choose appropriate backend for your use case
2. Follow established code patterns
3. Add tests for new functionality
4. Update relevant documentation

## Deployment

### PocketFlow Deployment
```bash
# Local development
python backend-new/run_server.py

# Production (Docker)
docker build -t research-agent -f backend-new/Dockerfile .
docker run -p 8000:8000 research-agent
```

### LangGraph Deployment
```bash
# Development
make dev

# Production
GEMINI_API_KEY=xxx LANGSMITH_API_KEY=xxx docker-compose up
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.