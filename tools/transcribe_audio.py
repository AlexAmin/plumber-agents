"""
Audio transcription using Gemini.
"""

import os
import tempfile
import requests
from pathlib import Path
from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig, Part


def transcribe_audio_from_url(audio_url: str, access_token: str) -> Optional[str]:
    """
    Download audio from URL and transcribe to text.

    Args:
        audio_url: URL to download the audio file
        access_token: Authorization token for downloading

    Returns:
        Transcribed text or None if failed
    """
    print(f"[TRANSCRIBE] Downloading audio from URL")

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / "audio.ogg"

        # Download audio
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(audio_url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                f.write(response.content)

            print(f"[TRANSCRIBE] Downloaded to {temp_path}")
        except Exception as e:
            print(f"[TRANSCRIBE] ❌ Download failed: {e}")
            return None

        # Transcribe using Gemini
        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

            # Upload file
            audio_file = client.files.upload(file=str(temp_path))
            print(f"[TRANSCRIBE] Uploaded to Gemini")

            # Generate transcription
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Transcribe this audio. Output only the spoken text without any changes.",
                    Part.from_uri(file_uri=audio_file.uri, mime_type="audio/ogg")
                ],
                config=GenerateContentConfig(
                    system_instruction="You are speech to text. Recognize the spoken language and output it without any changes"
                )
            )

            transcribed_text = (response.text or "").strip()
            print(f"[TRANSCRIBE] ✓ Done")

            # Cleanup
            client.files.delete(name=audio_file.name)

            return transcribed_text

        except Exception as e:
            print(f"[TRANSCRIBE] ❌ Transcription failed: {e}")
            return None
