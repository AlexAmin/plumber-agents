import os
from google import genai
from google.genai import Client
from google.genai.types import GenerateContentConfig
from tools.process_billing import process_billing


class OfficeAgent:
    """Office Agent - Handles billing validation and office workflows."""
    system_prompt: str = ""
    client: Client


    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        # Load system prompt from shared prompts directory
        prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/office_system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        print("[OfficeAgent] Initialized")

    def process(self, message: str) -> str:
        """
        Process message with orchestrator's history context.
        Agent is stateless - all history comes from the orchestrator.
        """
        try:
            print(f"[OfficeAgent] Processing: {message}...")
            response_text = self.client.models.generate_content(
                contents=message,
                model="gemini-2.5-flash",
                config=GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=[process_billing]
                )
            ).text
            print(f"[OfficeAgent] Response: {response_text[:100]}...")
            return response_text

        except Exception as e:
            print(f"[OfficeAgent] Error: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"
