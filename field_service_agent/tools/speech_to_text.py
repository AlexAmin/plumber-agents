def speech_to_text_transcriber(audio_file: str) -> dict:
    """
    Converts an audio file into a text string.
    NOTE: This is a mock implementation.
    """
    # In a real scenario, this would process the audio file.
    # For this simulation, we return a hardcoded transcript.
    transcription = "Hi, Frank here. I'm done with customer Meier at Schillerstrasse 12. I repaired the sink pipe. It took 1.5 hours of work plus the new gasket (item 10-B). The customer also signed on site."
    return {"transcription": transcription}