"""
Field Service Agent for ADK
Handles technician interactions and field service tasks.
"""

import sys
import os
from google.adk.agents import Agent
from tools.find_customer import find_customer
from tools.check_invoice_status import check_invoice_status

# Load system prompt from the shared prompts directory
prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/field_service_system_prompt.md")
with open(prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

field_service_agent = Agent(
    name="field_service_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist agent for handling field service technician interactions. "
        "Can look up customer information, check invoice statuses, and assist "
        "technicians with job-related queries."
    ),
    instruction=SYSTEM_PROMPT,
    tools=[find_customer, check_invoice_status],
)
