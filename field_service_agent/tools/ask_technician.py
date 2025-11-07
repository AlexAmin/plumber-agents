def ask_technician(question: str) -> str:
    """
    Use this tool to ask the technician (the user) a question, show them information for validation, or get their confirmation.
    The agent's question will be printed, and the user's typed response will be returned.
    """
    print(f"\n[Output] Agent A: {question}")
    response = input("[Input] Frank: ")
    return response
