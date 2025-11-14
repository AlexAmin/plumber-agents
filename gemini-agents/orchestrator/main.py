import os
import json
from typing import Dict, List

from google import genai
from google.genai import Client
from google.genai.types import Content, Part, GenerateContentResponse, GenerateContentConfig
from vertexai.generative_models import ChatSession

from tools.communicate_with_human import make_communicate_with_human_tool
from tools.field_service_agent import make_field_service_agent_tool
from tools.office_agent import make_office_agent_tool
from shared.users import USER_REGISTRY
from shared.orchestrator.whatsapp_handler import WhatsAppHandler
from shared.orchestrator.firestore_history import FirestoreHistory


class Orchestrator:
    chat_history: Dict[str, List[Content]] = {}
    chats: Dict[str, ChatSession] = {}
    orchestrator_prompt: str = ""
    client: Client
    firestore: FirestoreHistory

    def __init__(self):
        print("🚀 Orchestrator initializing...")
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        # Load System Prompt from the shared prompts directory
        prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/orchestrator_system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.orchestrator_prompt = f.read()

        # Initialize Firestore and load chat histories
        print("📥 Loading chat histories from Firestore...")
        self.firestore = FirestoreHistory()
        self.chat_history = self.firestore.load_all_histories()
        print(f"✓ Loaded histories for {len(self.chat_history)} users")

        # Setup WhatsApp handler
        # Pass the *instance method* as the callback
        self.whatsapp_handler = WhatsAppHandler(self.process_message)

        print("✓ Orchestrator ready.")

    def _serialize_history(self, user_role: str) -> List[Dict[str, str]]:
        """Convert Content objects to JSON-serializable dicts for a specific user."""
        history = self.chat_history.get(user_role, [])
        return [{"role": msg.role, "parts": [getattr(p, "text", "") for p in msg.parts]} for msg in history]

    def process_message(self, user_role: str, message: str) -> str:
        """
        Processes an incoming message from a user and returns the response.
        This is the main entry point for both CLI and WhatsApp.
        """
        try:
            # Get user info
            user = USER_REGISTRY.get(user_role)
            if not user:
                return f"❌ Unknown user: {user_role}. Please register first."

            print(f"[ORCHESTRATOR] Processing message from {user['name']}: {message}")
            # Build message with user context - inject current user info dynamically
            user_message = f"[User: {user['name']}, Role: {user['role']}]\n{message}"

            # Add a user message to the chat history
            self.append_chat_message(user_role, Content(role="user", parts=[Part(text=user_message)]))

            # Create tool factories with this user's history
            field_service_tool = make_field_service_agent_tool(lambda: self._serialize_history(user_role))
            office_tool = make_office_agent_tool(lambda: self._serialize_history(user_role))
            communicate_with_human = make_communicate_with_human_tool(self.append_chat_message)

            # Send the message
            response = self.client.models.generate_content(
                contents=self.chat_history[user_role],

                model="gemini-2.5-flash",
                config=GenerateContentConfig(
                    system_instruction=self.orchestrator_prompt,
                    tools=[field_service_tool, office_tool, communicate_with_human]
                )
            )

            # Add model response to history
            # This is the internal monologue, wdont need this
            # self.append_chat_message(user_role, Content(role="model", parts=response.parts))

            # Save the full updated history to Firestore to also include agent-to-agent chats
            for role in self.chat_history:
                print("save", role)
                self.firestore.save_history(role, self.chat_history[role])

            print(f"[ORCHESTRATOR] Model Response: {response.text}")
            return response.text
        except Exception as e:
            print(f"[ORCHESTRATOR] ❌ Error: {e}")
            return f"Sorry, an error occurred: {str(e)}"

    def append_chat_message(self, user_role: str, content: Content):
        if user_role not in self.chat_history:
            self.chat_history[user_role] = []
        print("append_chat_message", user_role, content.parts[0].text)
        self.chat_history[user_role].append(content)

    def run_cli(self):
        """
        Main orchestrator loop for handling CLI input.
        WhatsApp messages are handled separately via the webhook callback.
        """
        # Select user role at startup
        print("\n" + "─" * 60)
        print("👤 Who are you?")
        print("  1. Technician")
        print("  2. Office Staff")
        choice = input("\nSelect (1 or 2): ").strip()
        user_id = "technician" if choice == "1" else "office"
        user_name = USER_REGISTRY[user_id]['name']
        user_role = USER_REGISTRY[user_id]["role"]

        print(f"\n✓ You are: {user_name}\n")
        print("🚀 Ready for messages (CLI + WhatsApp)...\n")

        try:
            while True:
                # Get user input
                user_input = input(f"[{user_id.upper()}] Message: ").strip()

                if not user_input:
                    continue

                # Handle quit command
                if user_input.lower() == "quit":
                    print("\n👋 Goodbye!")
                    break

                # Process through Gemini orchestrator
                response = self.process_message(user_id, user_input)

                if response is None:
                    continue

                # Print response
                print(f"\n{'─' * 60}")
                print(f"💬 RESPONSE:")
                print(f"{'─' * 60}")
                print(response)
                print(f"{'─' * 60}\n")

        except KeyboardInterrupt:
            print("\n\n⏹️  Orchestrator stopped")


# --- Main execution ---
if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run_cli()
