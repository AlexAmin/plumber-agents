"""
Reusable HTTP server framework for AI agents.
Provides standard endpoints and structure for agent services.
"""
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Callable, Optional
import uvicorn


class AgentServer:
    """
    Base HTTP server for AI agents.
    Provides standard endpoints and handles request/response formatting.
    """

    def __init__(
            self,
            agent_name: str,
            request_callback: Callable[[str], str],
            port: int = 8010
    ):
        """
        Initialize agent server.
        """
        self.agent_name = agent_name
        self.request_callback = request_callback
        self.port = port

        # Create FastAPI app
        self.app = FastAPI(
            title=f"{agent_name} Agent",
            description=f"HTTP API for {agent_name}"
        )

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register standard agent endpoints."""

        @self.app.get("/")
        async def root():
            """Root endpoint - agent info."""
            return {
                "agent": self.agent_name,
                "status": "running",
                "endpoints": {
                    "POST /process": "Process a message",
                    "POST /process_job": "Process job data (if supported)",
                    "GET /health": "Health check"
                }
            }

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "agent": self.agent_name
            }

        @self.app.post("/process")
        async def process_message(request: Request):
            """Process a message from the orchestrator"""
            data = await request.json()
            print(f"[{self.agent_name}] Received message {data}")
            # Call handler
            response = self.request_callback(json.dumps(data))
            return JSONResponse(content=response)

    def run(self, host: str = "0.0.0.0"):
        """
        Start the agent server.

        Args:
            host: Host to bind to (default: 0.0.0.0 for all interfaces)
        """
        print(f"\n{'=' * 60}")
        print(f"🚀 {self.agent_name} Agent Server Starting")
        print(f"{'=' * 60}")
        print(f"   Port: {self.port}")
        print(f"   URL: http://localhost:{self.port}")
        print(f"   Docs: http://localhost:{self.port}/docs")
        print(f"{'=' * 60}\n")

        uvicorn.run(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )


def create_agent_server(
        agent_name: str,
        request_callback: Callable[[str], str],
        port: int
) -> AgentServer:
    """
    Helper to create an agent server from an agent class.
    """
    # Create server
    return AgentServer(
        agent_name=agent_name,
        request_callback=request_callback,
        port=port
    )
