"""Start the PocketFlow research agent server."""

import uvicorn
import os
from pathlib import Path

# Add src to Python path
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from src.app import app

if __name__ == "__main__":
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. Copy .env.example to .env and configure your settings.")
        print("   Example: cp .env.example .env")
    
    # Start server
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting PocketFlow Research Agent Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   API Docs: http://{host}:{port}/docs")
    print(f"   Frontend: http://{host}:{port}/app")
    
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["src"]
    )