import os
from google import genai
from google.genai import Client
from google.genai.types import GenerateContentConfig, AutomaticFunctionCallingConfig
from tools.find_customer import find_customer
from tools.check_invoice_status import check_invoice_status


class FieldServiceAgent:
    """Field Service Agent - handling technician interactions."""
    system_prompt: str = ""
    client: Client

    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        # Load system prompt from shared prompts directory
        prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/field_service_system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        print("[FieldServiceAgent] Initialized (stateless)")

    def process(self, message: str) -> str:
        """
        Process message with orchestrator's history context.
        Agent is stateless - all history comes from orchestrator.
        """
        try:
            print(f"[FieldServiceAgent] Processing: {message}...")
            response_text = self.client.models.generate_content(
                contents=message,
                model="gemini-2.5-flash",
                config=GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=[find_customer, check_invoice_status],
                    automatic_function_calling=AutomaticFunctionCallingConfig(disable=False)
                )
            ).text
            print(f"[FieldServiceAgent] Response: {response_text[:100]}...")
            return response_text

        except Exception as e:
            print(f"[FieldServiceAgent] Error: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"
