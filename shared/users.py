# User registry - maps phone numbers to user roles
# In production, this would be a database
USER_REGISTRY = {
    "491718398683": {
        "role": "technician",
        "name": "Michael",
        "default_agent": "field_service",
        "whatsapp": "491718398683"
    },
    "19712187997": {
        "role": "office",
        "name": "Klaus",
        "default_agent": "office",
        "whatsapp": "19712187997"
    },
    # CLI mode users
    "technician": {
        "role": "technician",
        "name": "Technician (CLI)",
        "default_agent": "field_service"
    },
    "office": {
        "role": "office",
        "name": "Office Staff (CLI)",
        "default_agent": "office"
    }
}


def get_whatsapp_numbers_for_role(user_role: str) -> list[str]:
    """ Send WhatsApp message to a recipient"""
    whatsapp_numbers = [
        phone
        for phone, details in USER_REGISTRY.items()
        if details.get("role") == user_role and details.get("whatsapp") is not None
    ]
    return whatsapp_numbers
