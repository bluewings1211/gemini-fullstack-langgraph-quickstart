"""FastAPI application for PocketFlow research agent."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

try:
    from .flow import run_research_agent
except ImportError:
    from flow import run_research_agent

app = FastAPI(title="Research Agent API", version="1.0.0")

# Pydantic models for API
class ResearchRequest(BaseModel):
    question: str
    context: Optional[str] = ""
    
class ResearchResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    research_summary: dict

# API Routes
@app.post("/api/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest):
    """Perform research and return answer with sources."""
    try:
        result = run_research_agent(
            question=request.question,
            context=request.context or ""
        )
        return ResearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "research-agent"}

# Static file serving for frontend
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    
    @app.get("/app/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend application."""
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            # Return index.html for SPA routing
            return FileResponse(frontend_dist / "index.html")

@app.get("/")
async def root():
    """Root endpoint - redirect to app."""
    if frontend_dist.exists():
        return FileResponse(frontend_dist / "index.html")
    else:
        return {
            "message": "Research Agent API", 
            "docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)