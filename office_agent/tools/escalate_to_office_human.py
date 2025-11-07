import json

def escalate_to_office_human(auftrags_id: str, message: str, options: list):
    """Sends a formatted message to an internal system (e.g., Slack, Teams, or a dashboard)
    where an office employee must make a yes/no decision.

    Args:
        auftrags_id: The ID of the job, e.g., "JOB-789-001".
        message: The question formulated by the LLM, e.g., "Conflict with Job 789: 0.5h too much (Contract Plus). Grant goodwill?".
        options: A list of options, e.g., ['Grant goodwill', 'Reject'].
    """
    print(f"--- HUMAN INTERVENTION REQUIRED ---")
    print(f"Job ID: {auftrags_id}")
    print(f"Message: {message}")
    print(f"Options: {options}")
    print(f"-------------------------------------")
    # In a real system, this would trigger a notification.
    # For this simulation, we'll just return a status.
    return {"escalation_status": "gesendet"}
