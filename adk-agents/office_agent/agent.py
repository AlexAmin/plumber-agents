"""
Office Agent for ADK
Handles billing validation and office workflows.
"""

import sys
import os

from google.adk import Agent
from tools.process_billing import process_billing

# Load system prompt from shared prompts directory
prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/office_system_prompt.md")
with open(prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

office_agent = Agent(
    name="office_agent",
    model="gemini-2.5-flash",
    description=(
        "Specialist agent for handling office and billing operations. "
        "Processes billing rules, validates contracts, and manages goodwill approvals "
        "according to company policies."
    ),
    instruction=SYSTEM_PROMPT,
    tools=[process_billing],
)
