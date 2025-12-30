"""
Web server for Agentic Platform UI
Provides a Lovable/Replit-like interface for building and deploying apps
"""

import asyncio
import json
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from app.agent import (
    PlatformAgent,
    BrowserAgent,
    DataAnalysisAgent,
    MCPAgent,
    FullStackShipAgent,
    TestAgent,
)
from loguru import logger

# FastAPI app
app = FastAPI(
    title="Agentic Platform",
    description="AI Agent Framework with Lovable-like UI",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent types
AGENT_TYPES = {
    "platform": PlatformAgent,
    "browser": BrowserAgent,
    "data": DataAnalysisAgent,
    "mcp": MCPAgent,
    "ship": FullStackShipAgent,
    "test": TestAgent,
}

# Active sessions
active_sessions = {}


class TaskRequest(BaseModel):
    agent_type: str = "platform"
    prompt: str
    max_steps: int = 20
    session_id: Optional[str] = None


class SessionInfo(BaseModel):
    session_id: str
    agent_type: str
    status: str
    created_at: str
    prompt: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    return FileResponse("ui/index.html")


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/agents")
async def list_agents():
    """List available agent types"""
    return {
        "agents": [
            {
                "id": "platform",
                "name": "Platform Agent",
                "description": "General-purpose agent with all tools",
                "icon": "🤖",
            },
            {
                "id": "browser",
                "name": "Browser Agent",
                "description": "Web automation and scraping specialist",
                "icon": "🌐",
            },
            {
                "id": "data",
                "name": "Data Analysis Agent",
                "description": "Data analysis and visualization expert",
                "icon": "📊",
            },
            {
                "id": "mcp",
                "name": "MCP Agent",
                "description": "Model Context Protocol for external tools",
                "icon": "🔌",
            },
            {
                "id": "ship",
                "name": "FullStack Ship Agent",
                "description": "Complete SaaS builder (Supabase + Stripe)",
                "icon": "🚀",
            },
            {
                "id": "test",
                "name": "Test Agent",
                "description": "Validates all components and dependencies",
                "icon": "🧪",
            },
        ]
    }


@app.get("/api/sessions")
async def list_sessions():
    """List active sessions"""
    return {"sessions": list(active_sessions.values())}


@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Create a new task"""
    session_id = request.session_id or datetime.now().strftime("%Y%m%d%H%M%S%f")

    # Validate agent type
    if request.agent_type not in AGENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    # Create session info
    session_info = {
        "session_id": session_id,
        "agent_type": request.agent_type,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "prompt": request.prompt,
        "max_steps": request.max_steps,
    }

    active_sessions[session_id] = session_info

    return {"session_id": session_id, "status": "created"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time agent communication"""
    await websocket.accept()

    try:
        # Get session info
        if session_id not in active_sessions:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            return

        session = active_sessions[session_id]
        agent_type = session["agent_type"]
        prompt = session["prompt"]
        max_steps = session.get("max_steps", 20)

        # Update status
        session["status"] = "running"
        await websocket.send_json(
            {"type": "status", "status": "initializing", "message": "Creating agent..."}
        )

        # Create agent
        agent_class = AGENT_TYPES[agent_type]
        agent = await agent_class.create(max_steps=max_steps)

        await websocket.send_json(
            {
                "type": "status",
                "status": "running",
                "message": f"Agent created with {len(agent.tool_collection.tools)} tools",
            }
        )

        # Run agent with streaming updates
        await websocket.send_json(
            {"type": "agent_start", "agent": agent_type, "prompt": prompt}
        )

        # Execute task
        try:
            # Run agent (we'll need to modify this to stream updates)
            response = await agent.run(prompt)

            # Send final response
            await websocket.send_json(
                {
                    "type": "response",
                    "response": response,
                    "steps_used": agent.current_step,
                    "max_steps": max_steps,
                    "state": agent.state.value,
                }
            )

            # Update session
            session["status"] = "completed"
            session["response"] = response

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            await websocket.send_json({"type": "error", "message": str(e)})
            session["status"] = "error"
            session["error"] = str(e)

        finally:
            await agent.cleanup()
            await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return active_sessions[session_id]


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Session not found")


# Mount static files (UI)
try:
    app.mount("/ui", StaticFiles(directory="ui"), name="ui")
except:
    logger.warning("UI directory not found, static files not mounted")


if __name__ == "__main__":
    logger.info("Starting Agentic Platform Web Server...")
    logger.info("UI will be available at: http://localhost:8005")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
    )
