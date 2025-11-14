"""
WhatsApp message handler for the orchestrator.
Manages incoming/outgoing WhatsApp messages and webhook server.
"""

import os
import json
import threading
from typing import Callable

from shared.whatsapp_client import WhatsAppClient
from shared.users import USER_REGISTRY
from shared.orchestrator.webhook_server import WebhookServer
from tools.transcribe_audio import transcribe_audio_from_url


class WhatsAppHandler:
    """Handles incoming WhatsApp communication for the orchestrator."""
    message_callback: Callable[[str, str], str]
    whatsapp_client: WhatsAppClient

    def __init__(self, message_callback: Callable[[str, str], str]):
        """Initialize WhatsApp handler."""
        self.message_callback = message_callback
        self.whatsapp_client = WhatsAppClient()

        # Start webhook server in background
        self.webhook_server = WebhookServer(
            message_callback=self._handle_incoming_message
        )
        self._start_webhook_server()

    def _start_webhook_server(self):
        """Start webhook server in background thread."""

        def run_server():
            port = int(os.getenv('WEBHOOK_PORT', 8010))
            self.webhook_server.run(port=port, host="0.0.0.0")

        webhook_thread = threading.Thread(target=run_server, daemon=True)
        webhook_thread.start()
        print(f"[WHATSAPP] Webhook server started in background")

    def _process_message(self, message_content: str) -> str:
        """
        Process WhatsApp message - transcribe if audio, otherwise return as-is.
        """
        try:
            # Check if it's a media message
            media_data = json.loads(message_content)

            if isinstance(media_data, dict) and media_data.get("type") == "audio":
                # Get audio URL from WhatsApp
                media_id = media_data["media_id"]
                audio_url = self.whatsapp_client.get_media_url(media_id)

                if not audio_url:
                    return "Sorry, couldn't get the audio file."

                # Transcribe audio
                transcribed = transcribe_audio_from_url(
                    audio_url,
                    self.whatsapp_client.access_token
                )
                return transcribed if transcribed else "Sorry, I couldn't transcribe the audio."

            # Other media types
            return f"Received a {media_data.get('type')}, but I can only process audio."

        except (json.JSONDecodeError, TypeError):
            # Plain text message
            return message_content

    def _handle_incoming_message(self, from_number: str, message_content: str):
        """
        Callback for when a WhatsApp message is received.
        Processes message and delegates to orchestrator via callback.

        Args:
            from_number: Sender's phone number
            message_content: Message text or media info (as JSON)
        """
        # Determine user ID from phone number
        user_id = from_number if from_number in USER_REGISTRY else from_number
        user = USER_REGISTRY.get(user_id, {"name": from_number, "role": "unknown"})

        print(f"\n{'=' * 60}")
        print(f"📱 WhatsApp message from {user.get('name', from_number)}")
        print(f"{'=' * 60}")

        # Check if message is audio and transcribe if needed
        processed_message = self._process_message(message_content)

        print(f"Message: {processed_message[:100]}")
        print(f"{'=' * 60}\n")

        # Delegate to orchestrator via callback
        # Callback signature: callback(user_id: str, message: str)
        try:
            response = self.message_callback(user.get("role"), processed_message)

            # Send response back via WhatsApp
            if response:
                phone_for_reply = from_number.lstrip("+")
                self.whatsapp_client.send(phone_for_reply, response)
                print(f"[WHATSAPP] Sent response to {user.get('name', from_number)}\n")
        except Exception as e:
            print(f"[WHATSAPP] Error in message callback: {e}\n")
            # Try to send error message back
            try:
                phone_for_reply = from_number.lstrip("+")
                self.whatsapp_client.send(phone_for_reply, "Sorry, I encountered an error processing your message.")
            except:
                pass
