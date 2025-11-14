"""
Tool for calling the Field Service Agent.
Used by the orchestrator to route technician messages.
"""
from typing import Callable, List, Dict
import requests


def make_field_service_agent_tool(get_history: Callable[[], List[Dict]]):
    """
    Factory function that creates a field_service_agent tool with history context.

    Args:
        get_history: Callback to get current conversation history

    Returns:
        Function that calls the field service agent with injected history
    """

    def field_service_agent(message: str) -> str:
        """
        Call the Field Service Agent to handle technician messages.

        Use this tool when:
        - A technician is reporting job completion
        - A technician needs to look up customer information
        - A technician is documenting field work
        - Any message from a user with role 'technician'

        The field service agent will:
        - Collect job data (customer, location, work done)
        - Look up customer records
        - Prepare data for billing handoff

        Args:
            message: The technician's message to process

        Returns:
            str: Plain text response from the agent
        """
        url = "http://localhost:8001/process"

        payload = {
            "message": message,
            "context": get_history()
        }

        print(f"[TOOL] Calling field_service_agent: {message[:50]}...")

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                # The agent server wraps text responses in {"message": "...", "status": "success"}
                response_data = response.json()
                # Extract the message field
                if isinstance(response_data, dict) and "message" in response_data:
                    response_text = response_data["message"]
                elif isinstance(response_data, str):
                    response_text = response_data
                else:
                    response_text = str(response_data)

                print(f"[TOOL] Field service agent responded: {response_text[:100]}...")
                return response_text
            else:
                error_msg = f"Field service agent failed to respond (HTTP {response.status_code})"
                print(f"[TOOL] Warning: {error_msg}")
                return error_msg

        except requests.ConnectionError:
            error_msg = "Cannot connect to field service agent (is it running on port 8001?)"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg
        except requests.Timeout:
            error_msg = "Field service agent timeout (exceeded 30 seconds)"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Error calling field service agent: {str(e)}"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg

    return field_service_agent
