import os
import google.generativeai as genai
from tools.tools import get_current_weather

# IMPORTANT: Set your API key either as an environment variable or directly here.
# For example:
# genai.configure(api_key="YOUR_API_KEY")
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
else:
    print("Please set the GEMINI_API_KEY environment variable or configure the API key directly in the script.")
    exit()

# Dictionary of available tools
available_tools = {
    "get_current_weather": get_current_weather,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=list(available_tools.values())
)

chat = model.start_chat()

# Initial prompt
prompt = "What is the weather like in Boston?"
print(f"You: {prompt}")

while True:
    # Send the prompt to the model
    response = chat.send_message(prompt)

    # Check for function calls in the response parts
    has_function_call = any(part.function_call for part in response.candidates[0].content.parts)

    if has_function_call:
        # The model decided to call one or more tools
        tool_responses = []
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_call = part.function_call
                tool_name = function_call.name
                
                if tool_name in available_tools:
                    tool_function = available_tools[tool_name]
                    args = {key: value for key, value in function_call.args.items()}
                    
                    print(f"Tool call: {tool_name}(**{args})")
                    
                    # Call the tool function
                    tool_response_data = tool_function(**args)
                    
                    # Append the tool response to send back to the model
                    tool_responses.append(
                        {
                            "function_response": {
                                "name": tool_name,
                                "response": tool_response_data,
                            }
                        }
                    )
        
        # Send the tool responses back to the model
        prompt = tool_responses

    else:
        # The model did not call a tool, print the text response
        print(f"Gemini: {response.text}")
        
        # Prompt the user for the next message
        user_input = input("You: ")
        if not user_input:
            print("Exiting.")
            break
        prompt = user_input
