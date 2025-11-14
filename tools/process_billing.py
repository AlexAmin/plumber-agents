import json
import random
from typing import List, Dict


def process_billing(title: str, customer: str, items: list[str]):
    """Process billing a job. Will also automatically return price information

    Args:
        title: The title/description of the billing rule
        customer: The customer ID or name
        items: List of items with name and price to be billed
    Returns:
        dict: Result containing:
            - status: Success/failure of billing process
            - total: Total amount to be billed
            - items: Processed list of items
    """
    items = [
        {
            "name": item,
            "price": f"{round(random.uniform(0.1, 100), 2)} Euro"
        }
        for item in items
    ]

    return {
        "status": "success",
        "customer": customer,
        "title": title,
        "items": items
    }
