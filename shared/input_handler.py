import os
import urllib.parse
import urllib.request
import tempfile
import mimetypes
from pathlib import Path
from typing import Callable

def get_processed_input(input_str: str, transcriber: Callable[[str], str]):
    """
    Handles different input modalities by processing a string that can be text, a file path, or a URL.

    Args:
        input_str: The user's input string.
        transcriber: A function that takes a file path to an audio file and returns a transcription.

    Returns:
        The processed input, which can be a string (text or transcription) or bytes (for images).
    """
    try:
        parsed_url = urllib.parse.urlparse(input_str)

        if parsed_url.scheme in ['http', 'https']:
            with urllib.request.urlopen(input_str) as response:
                content_type = response.headers.get('content-type')
                if content_type and content_type.startswith('audio/'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(response.read())
                        tmp_file_path = tmp_file.name
                    try:
                        transcription = transcriber(tmp_file_path)
                    finally:
                        os.unlink(tmp_file_path)
                    return transcription
                elif content_type and content_type.startswith('image/'):
                    return response.read()
                else:
                    return response.read().decode('utf-8')

        elif parsed_url.scheme == 'file':
            file_path = Path(urllib.parse.unquote(parsed_url.path))
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('audio/'):
                return transcriber(str(file_path))
            else:
                return file_path.read_bytes()

        elif Path(input_str).exists():
            file_path = Path(input_str)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('audio/'):
                return transcriber(str(file_path))
            else:
                return file_path.read_bytes()
        else:
            # It's plain text
            if input_str == "pl":
                return get_processed_input("file:///Users/alex/git/plumber-agents/plumber-call.wav", transcriber)
            return input_str
    except Exception as e:
        return f"Error processing input: {e}"
