def find_customer(customer_name: str, customer_address: str) -> dict:
    customer_name = customer_name.strip().lower()
    customer_address = customer_address.strip().lower()
    """
    Use this tool to find a customer's unique ID and validate their details using the company's customer database.
    You must use this tool as soon as you have extracted a customer name and location from the technician's report.
    It is critical for linking the job to the correct customer account.

    If you cannot find a specific customer, you must retry with common misspellings like "Meier" or "Meyer" or "Mayer"

    """
    print(f"TOOL CALLED: find_customer(customer_name='{customer_name}', customer_address='{customer_address}')")
    if customer_name == "meier" and "schillerstrasse 12" in customer_address:
        return {
            "status": "found",
            "customer_id": "789",
            "full_name": "Klaus Meier",
            "full_address": "Schillerstrasse 12, 10117 Berlin"
        }
    else:
        return {
            "status": "not_found",
            "customer_id": None,
            "full_name": None,
            "full_address": None
        }
