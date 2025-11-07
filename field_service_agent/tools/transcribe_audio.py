import google.generativeai as genai

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes the given audio file using the Gemini 1.5 Flash model."""
    print(f"TOOL CALLED: transcribe_audio(audio_file_path='{audio_file_path}')")
    try:
        # Note: This uses the same API key configured in the main script.
        model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
        audio_file = genai.upload_file(path=audio_file_path)
        response = model.generate_content(
            ["Please transcribe this audio recording of a technician reporting job details.", audio_file],
            request_options={"timeout": 600} # Increased timeout for larger files
        )
        # It is good practice to delete the file after use
        genai.delete_file(audio_file.name)
        return response.text
    except Exception as e:
        return f"Error during transcription: {e}"
