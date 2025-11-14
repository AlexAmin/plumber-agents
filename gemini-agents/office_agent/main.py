"""
Office Agent HTTP Server
Handles billing validation and office workflows via HTTP API.
"""
from shared.agent_server import create_agent_server
from agent import OfficeAgent

if __name__ == "__main__":
    # Create and run agent server
    server = create_agent_server(
        agent_name="Office",
        request_callback=OfficeAgent().process,
        port=8002
    )

    server.run()
