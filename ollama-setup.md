# Ollama Setup Guide for Research Agent

## Recommended Models for Research Tasks

Based on performance and capability analysis, here are the recommended models:

### Primary Options (High Performance)
1. **DeepSeek-R1** - Excellent reasoning capabilities, approaching O3/Gemini 2.5 Pro performance
2. **Llama 3.3 70B** - Similar performance to Llama 3.1 405B but more efficient
3. **Phi-4 14B** - Microsoft's state-of-the-art model with strong reasoning

### Resource-Efficient Options
1. **Gemma 3** - Google's lightweight model, excellent for Q&A and reasoning
2. **Phi-2 2.7B** - Microsoft's compact model with outstanding reasoning capabilities

## Hardware Requirements

- **7B models**: Minimum 8GB RAM
- **13B models**: Minimum 16GB RAM  
- **33B+ models**: Minimum 32GB RAM
- **GPU**: Model size should be ≤ ⅔ of available VRAM

## Remote Setup Configuration

### 1. Environment Variables
```bash
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*
```

### 2. Service Configuration (Linux)
Add to `/etc/systemd/system/ollama.service`:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
```

### 3. Firewall Configuration
```bash
# Allow Ollama port
sudo ufw allow 11434
```

### 4. Model Installation
```bash
# Install recommended models
ollama pull deepseek-r1:latest
ollama pull llama3.3:70b
ollama pull phi4:latest
ollama pull gemma3:latest
```

## Integration with PocketFlow using Ollama Python Package

### 1. Install Ollama Python Package
```bash
pip install ollama
```

### 2. Python Client Setup
```python
import ollama

# Configure client for remote Ollama instance
client = ollama.Client(host='http://your-ollama-server:11434')

class OllamaLLMClient:
    def __init__(self, host="http://your-ollama-server:11434"):
        self.client = ollama.Client(host=host)
    
    def generate(self, model, prompt, system=None):
        """Generate completion using Ollama"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat(
            model=model,
            messages=messages
        )
        return response['message']['content']
    
    def chat(self, model, messages):
        """Chat with conversation history"""
        response = self.client.chat(
            model=model,
            messages=messages
        )
        return response['message']['content']
    
    def list_models(self):
        """List available models"""
        return self.client.list()
```

### 3. PocketFlow Node Integration Example
```python
from pocketflow import Node
import ollama

class OllamaNode(Node):
    def __init__(self, model_name, host="http://your-ollama-server:11434"):
        super().__init__()
        self.client = ollama.Client(host=host)
        self.model_name = model_name
    
    def exec(self, prep_res):
        prompt = prep_res.get('prompt', '')
        system = prep_res.get('system', None)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat(
            model=self.model_name,
            messages=messages
        )
        
        return {
            'response': response['message']['content'],
            'model': self.model_name
        }
```

## Model Selection Strategy

### For Different Research Tasks:
- **Query Generation**: `phi4` or `gemma3` (fast, efficient)
- **Web Research**: `deepseek-r1` (excellent reasoning)
- **Reflection/Analysis**: `llama3.3:70b` (comprehensive understanding)
- **Answer Synthesis**: `deepseek-r1` (strong reasoning and synthesis)

## Configuration for Backend

### Environment Variables (.env)
```bash
# Replace GEMINI_API_KEY with Ollama configuration
OLLAMA_HOST=http://your-ollama-server:11434
OLLAMA_QUERY_MODEL=phi4
OLLAMA_RESEARCH_MODEL=deepseek-r1
OLLAMA_REFLECTION_MODEL=llama3.3:70b
OLLAMA_ANSWER_MODEL=deepseek-r1
```

## Security Considerations

⚠️ **Important**: Only expose Ollama service on trusted networks
- Use VPN for remote access when possible
- Consider authentication proxy for production use
- Monitor resource usage and rate limiting

## Testing Connection

```python
import ollama

# Test connection to remote Ollama
client = ollama.Client(host='http://your-ollama-server:11434')

# List available models
models = client.list()
print("Available models:", [model['name'] for model in models['models']])

# Test generation
response = client.chat(
    model='gemma3',
    messages=[
        {'role': 'user', 'content': 'Explain quantum computing in simple terms'}
    ]
)
print("Response:", response['message']['content'])
```