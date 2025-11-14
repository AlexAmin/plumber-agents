"""
Tool for calling the Office Agent.
Used by the orchestrator to route office staff messages and process job handoffs.
"""
from typing import Callable, List, Dict

import requests
import sys
import os


def make_office_agent_tool(get_history: Callable[[], List[Dict]]):
    def office_agent(message: str = None, job_data: str = None) -> str:
        """
        Call the Office Agent to handle billing, compliance, and administrative tasks.

        Use this tool when:
        - An office staff member sends a message
        - A field service agent hands off completed job data
        - Billing validation or invoice creation is needed
        - Administrative tasks need to be handled

        The office agent will:
        - Validate billing information
        - Process job data for invoicing
        - Handle compliance checks
        - Escalate to human staff when needed

        Args:
            message: Message from office staff, orchestrator, or formatted job data
            job_data: Optional job data dict (included in context, but also passed separately)

        Returns:
            str: Plain text response from the agent
        """

        # Always use the /process endpoint
        url = "http://localhost:8002/process"

        # Build context array, including job_data if present
        payload = {
            "message": message,
            "job_data": job_data,
            "context": get_history()
        }

        try:
            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                response_data = response.json()
                # Extract the message field
                if isinstance(response_data, dict) and "message" in response_data:
                    response_text = response_data["message"]
                elif isinstance(response_data, str):
                    response_text = response_data
                else:
                    response_text = str(response_data)

                print(f"[TOOL] Office agent responded: {response_text[:100]}...")
                return response_text
            else:
                error_msg = f"Office agent failed to respond (HTTP {response.status_code})"
                print(f"[TOOL] Warning: {error_msg}")
                return error_msg

        except requests.ConnectionError:
            error_msg = "Cannot connect to office agent (is it running on port 8002?)"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg
        except requests.Timeout:
            error_msg = "Office agent timeout (exceeded 30 seconds)"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Error calling office agent: {str(e)}"
            print(f"[TOOL] Warning: {error_msg}")
            return error_msg
    return office_agent
