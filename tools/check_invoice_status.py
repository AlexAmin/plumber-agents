def check_invoice_status(customer_id: str) -> dict:
    """
    After finding the customer's ID with the 'find_customer' tool, use this tool to check for existing open invoices.
    This is a crucial step to prevent duplicate billing for the same job.
    The agent must always perform this check before asking the technician for validation.
    """
    print(f"TOOL CALLED: check_invoice_status(customer_id='{customer_id}')")
    if customer_id == "789":
        return {
            "status": "no_open_invoice",
            "existing_invoice_id": None
        }
    else:
        return {
            "status": "error",
            "existing_invoice_id": None
        }