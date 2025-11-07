import requests
import json

def send_data_to_office_agent(job_data: str):
    """Sends job data (as a JSON string) to the office agent for processing.

    Args:
        job_data: A JSON string containing the complete job details.
    """
    office_agent_url = "http://localhost:8001/process_job"
    try:
        # The input is a string, but the API expects a JSON object, so we parse it first.
        data_to_send = json.loads(job_data)

        print(f"--- Sending data to Office Agent ---")
        print(f"URL: {office_agent_url}")
        print(f"Data: {json.dumps(data_to_send, indent=2)}")

        response = requests.post(office_agent_url, json=data_to_send, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_json = response.json()
        print(f"--- Response from Office Agent ---")
        print(f"{json.dumps(response_json, indent=2)}")

        return response_json

    except requests.exceptions.RequestException as e:
        error_message = f"Error communicating with the Office Agent: {e}"
        print(error_message)
        return {"error": error_message}
    except json.JSONDecodeError as e:
        error_message = f"Error decoding the job_data string: {e}. Please ensure it is valid JSON."
        print(error_message)
        return {"error": error_message}
