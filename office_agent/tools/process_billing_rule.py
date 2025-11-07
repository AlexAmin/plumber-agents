import json

def process_billing_rule(job_data: str, force_kulanz: bool = False):
    """This is the deterministic (hard-coded) business logic.
    It is the "old API" that knows about contracts, hourly rates, and goodwill rules.
    It is *not* an LLM.

    Args:
        job_data: JSON string of the job data from Agent A.
        force_kulanz: Optional boolean, default: False. Set to True if the office human has approved the goodwill.
    """
    data = json.loads(job_data)
    auftrags_id = data.get("auftrags_id", "unknown")

    # Mock logic: Conflict if work_hours > 1 and force_kulanz is False
    if data.get("arbeit_stunden", 0) > 1 and not force_kulanz:
        return {
            "status": "konflikt",
            "auftrags_id": auftrags_id,
            "grund": "kulanz_pruefung_noetig",
            "details": f"{data.get('arbeit_stunden', 0) - 1}h too much according to contract Plus"
        }
    else:
        return {
            "status": "success",
            "auftrags_id": auftrags_id,
            "notiz": "Booked as goodwill" if force_kulanz else "Standard booking successful"
        }
