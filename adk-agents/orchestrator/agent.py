"""
ADK Orchestrator - Agent Definition for ADK Web UI
This file exposes the root_agent for the ADK web interface.
"""

import os
import sys

from google.adk.agents import Agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from tools.communicate_with_human import make_communicate_with_human_tool
from tools.find_customer import find_customer
from tools.check_invoice_status import check_invoice_status
from tools.process_billing import process_billing


# --- Prompts ---
def _load_prompt(filename):
    """Helper to load prompts from the shared prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), f"../../prompts/{filename}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


orchestrator_prompt = _load_prompt("orchestrator_system_prompt.md")
field_service_prompt = _load_prompt("field_service_system_prompt.md")
office_prompt = _load_prompt("office_system_prompt.md")

# --- Specialist Agents Definition ---

# Define agents directly in this file for a simplified, in-process architecture.
# This is ideal for demos and tightly-coupled systems.

field_service_agent = Agent(
    name="field_service_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist agent for handling field service technician interactions. "
        "Can look up customer information, check invoice statuses, and assist "
        "technicians with job-related queries."
    ),
    instruction=field_service_prompt,
    tools=[find_customer, check_invoice_status],
)

office_agent = Agent(
    name="office_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist agent for handling office and billing operations. "
        "Processes billing rules, validates contracts, and manages goodwill approvals "
        "according to company policies."
    ),
    instruction=office_prompt,
    tools=[process_billing],
)

# --- Orchestrator Agent Definition ---

# Create the orchestrator agent with instructions, tools, and sub-agents.
# This is the root_agent that ADK will run.

root_agent = Agent(
    name="orchestrator",
    model="gemini-2.5-flash",
    description=(
        "Main orchestrator agent that coordinates between field service and office operations. "
        "Routes user requests to the appropriate specialist agent based on the nature of the task."
    ),
    instruction=orchestrator_prompt,
    sub_agents=[field_service_agent, office_agent],
    tools=[make_communicate_with_human_tool(None)],
)
