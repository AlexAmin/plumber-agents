
def get_current_weather(location: str, unit: str = "celsius"):
    """Gets the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: The unit to use, either "celsius" or "fahrenheit"
    """
    return {"location": location, "temperature": "32", "unit": unit}
