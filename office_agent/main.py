import os
import sys
import json
import google.generativeai as genai
from fastapi import FastAPI, Request
import uvicorn

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from office_agent.tools.process_billing_rule import process_billing_rule
from office_agent.tools.escalate_to_office_human import escalate_to_office_human

# --- 1. Configuration ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("ERROR: The GEMINI_API_KEY environment variable was not found.")
genai.configure(api_key=api_key)

# --- 2. Load System Prompt and Define Tools ---
try:
    with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()
except FileNotFoundError:
    raise FileNotFoundError("ERROR: The prompt file 'prompts/system_prompt.txt' was not found.")

available_tools = {
    "process_billing_rule": process_billing_rule,
    "escalate_to_office_human": escalate_to_office_human,
}

# --- 3. Model Initialization ---
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_prompt,
    tools=list(available_tools.values())
)

# --- 4. FastAPI Server Definition ---
app = FastAPI()

@app.post("/process_job")

async def process_job_endpoint(request: Request):
    """Receives job data from Agent A, processes it, and returns the result."""
    job_data_json = await request.json()
    job_data_str = json.dumps(job_data_json)

    print(f"\n--- Received New Job ---")
    print(f"[Input] Received job data: {job_data_str}")

    # Start a new chat session for each request
    chat = model.start_chat(enable_automatic_function_calling=True)

    # Send the job data to the model
    response = chat.send_message(job_data_str)

    # The response from the model might be a function call or text.
    # The framework handles the function calls automatically.
    # The final text response is what we want to return.
    final_text = response.text

    print(f"[Output] Final response: {final_text}")
    print(f"--- Job Processing Complete ---")

    # Attempt to parse the final text as JSON to send back a structured response
    try:
        return json.loads(final_text)
    except json.JSONDecodeError:
        return {"status": "completed", "message": final_text}

def main():
    """Starts the Uvicorn server for the Office Agent."""
    print("--- Agent B (Office Agent) is starting as a web server. ---")
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()