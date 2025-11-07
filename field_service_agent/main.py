import os
import sys
import google.generativeai as genai
from tools.find_customer import find_customer
from tools.check_invoice_status import check_invoice_status
from tools.ask_technician import ask_technician
from tools.transcribe_audio import transcribe_audio
from tools.send_data_to_office_agent import send_data_to_office_agent

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from shared.input_handler import get_processed_input

def main():
    # --- 1. Configuration ---
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: The GEMINI_API_KEY environment variable was not found.")
        return
    genai.configure(api_key=api_key)

    # --- 2. Load System Prompt and Define Tools ---
    try:
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print("ERROR: The prompt file 'prompts/system_prompt.txt' was not found.")
        return

    available_tools = {
        "find_customer": find_customer,
        "check_invoice_status": check_invoice_status,
        "ask_technician": ask_technician,
        "send_data_to_office_agent": send_data_to_office_agent,
    }

    # --- 3. Model Initialization ---
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt,
        tools=list(available_tools.values())
    )
    # Enable automatic function calling to let the model drive the conversation
    chat = model.start_chat(enable_automatic_function_calling=True)

    # --- 4. Endless Chat Loop ---
    print("--- Agent A is running in an endless chat loop. ---")
    print("--- Provide input (text, file path, or URL) to start a new job workflow. ---")

    while True:
        user_input = input("\nEnter job input (or type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            print("Exiting agent.")
            break
        
        print("\n--- Starting New Job Workflow ---")
        
        processed_input = get_processed_input(user_input, transcriber=transcribe_audio)
        
        if isinstance(processed_input, str) and processed_input.startswith("Error"):
            print(f"[Error] Could not process input: {processed_input}")
            continue
        
        message_parts = []
        if isinstance(processed_input, bytes):
            print(f"[Input] Using file content.")
            message_parts.append(processed_input)
        else:
            print(f"[Input] Using text: {processed_input}")
            message_parts.append(processed_input)

        # The model can handle a list of parts, including text and images
        final_response = chat.send_message(message_parts)

        # 3. Workflow for the job is complete
        print("\n--- Job Workflow Complete ---")
        if final_response.text:
            print(f"Final model output: {final_response.text}")
        print("---------------------------------")

if __name__ == "__main__":
    main()
