"""
Field Service Agent HTTP Server
Handles technician messages and job data collection via HTTP API.
"""
from agent import FieldServiceAgent
from shared.agent_server import create_agent_server

if __name__ == "__main__":
    # Create and run agent server
    server = create_agent_server(
        agent_name="FieldService",
        request_callback=FieldServiceAgent().process,
        port=8001,
    )

    server.run()
