"""
WhatsApp webhook server for receiving incoming messages.
Receives messages from Meta's WhatsApp Cloud API and routes to agents.
"""

import os
import json
import hmac
import hashlib
import uvicorn
import asyncio
from fastapi import FastAPI, Request, Response
from typing import Dict, Callable, Optional
from queue import Queue


class WebhookServer:
    """
    A FastAPI-based server to handle WhatsApp webhooks.
    """

    def __init__(self, message_callback: Optional[Callable] = None):
        """
        Initialize webhook server.

        Args:
            message_callback: Function to call when message received.
                            Signature: callback(from_number: str, message_content: str)
        """
        self.app = FastAPI(title="WhatsApp Webhook Server")
        self.message_callback = message_callback
        # Track processed message IDs to prevent duplicate processing
        # WhatsApp webhooks can deliver the same message multiple times for reliability
        self.processed_message_ids = set()
        self._setup_routes()

    def _setup_routes(self):
        """Binds the API routes to their corresponding methods."""
        self.app.get("/")(self.root)
        self.app.get("/whatsapp/webhook")(self.webhook_verify)
        self.app.post("/whatsapp/webhook")(self.webhook_receive)
        self.app.get("/health")(self.health_check)

    async def root(self):
        """Root endpoint to confirm the server is running."""
        return {
            "message": "WhatsApp Webhook Server is running.",
            "docs": "/docs",
            "webhook_url": "/whatsapp/webhook"
        }

    def _verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook request is from Meta (security check).
        """
        app_secret = os.getenv("WHATSAPP_VERIFY_TOKEN")
        if not app_secret:
            print("⚠️  WHATSAPP_VERIFY_TOKEN not set - skipping signature verification (dev mode)")
            return True

        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, f'sha256={expected_signature}')

    async def webhook_verify(self, request: Request):
        """
        Webhook verification endpoint (required by Meta).
        """
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

        if mode == "subscribe" and token == verify_token:
            print(f"✓ Webhook verified successfully")
            return Response(content=challenge, media_type='text/plain')
        else:
            print(f"✗ Webhook verification failed (mode={mode}, token_match={token == verify_token})")
            return Response(content='Forbidden', status_code=403)

    async def webhook_receive(self, request: Request):
        """
        Receives incoming WhatsApp messages from Meta.
        """
        body = await request.body()
        signature = request.headers.get('X-Hub-Signature-256', '')

        #if not self._verify_webhook_signature(body, signature):
        #    print(f"✗ Invalid webhook signature - rejecting request {signature}")
        #    return Response(content='Invalid signature', status_code=403)

        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in webhook: {e}")
            return Response(content='Invalid JSON', status_code=400)

        # Process incoming messages
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                self._process_messages(value)
                self._process_statuses(value)

        return {"status": "ok"}

    def _process_messages(self, value: Dict):
        """Processes the 'messages' part of the webhook payload."""
        for message in value.get('messages', []):
            from_number = message.get('from')
            message_id = message.get('id')
            message_type = message.get('type')

            # Skip duplicate messages - WhatsApp may send the same message_id multiple times
            # Without this check, we'd process the same message repeatedly, causing infinite loops
            if message_id in self.processed_message_ids:
                print(f"⏭️  Skipping duplicate message {message_id}")
                continue

            message_content = self._extract_message_content(message)

            if from_number and message_content:
                print(f"📨 Received from {from_number}: {message_content[:100]}")

                # Mark as processed BEFORE calling callback to prevent race conditions
                self.processed_message_ids.add(message_id)

                # Call the message callback if provided
                if self.message_callback:
                    self.message_callback(from_number, message_content)

    def _extract_message_content(self, message: Dict) -> str | None:
        """Extracts content from a message object based on its type."""
        message_type = message.get('type')

        if message_type == 'text':
            return message.get('text', {}).get('body')
        elif message_type == 'button':
            return message.get('button', {}).get('payload')
        elif message_type == 'interactive':
            interactive = message.get('interactive', {})
            if 'button_reply' in interactive:
                return interactive['button_reply']['id']
            elif 'list_reply' in interactive:
                return interactive['list_reply']['id']
        elif message_type in ['image', 'audio', 'document', 'video', 'sticker']:
            media_id = message.get(message_type, {}).get('id')
            # Return a JSON string for media messages
            return json.dumps({
                "type": message_type,
                "media_id": media_id
            })
        elif message_type == 'location':
            location = message.get('location', {})
            lat = location.get('latitude')
            lon = location.get('longitude')
            return f"[LOCATION:{lat},{lon}]"
        else:
            print(f"⚠️  Unsupported message type: {message_type}")
            return None

    def _process_statuses(self, value: Dict):
        """Processes the 'statuses' part of the webhook payload."""
        for status in value.get('statuses', []):
            recipient_id = status.get('recipient_id')
            status_type = status.get('status')
            message_id = status.get('id')
            print(f"📬 Status update: message {message_id} to {recipient_id} is {status_type}")

    async def health_check(self):
        """Health check endpoint."""
        return {"status": "healthy"}

    def run(self, port: int, host: str = "0.0.0.0"):
        """Starts the Uvicorn server."""
        print(f"""
{'=' * 70}
🚀 Starting WhatsApp Webhook Server
{'=' * 70}

Webhook URL: http://{host}:{port}/whatsapp/webhook
Health Check: http://{host}:{port}/health

{'=' * 70}
        """)
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = WebhookServer()
    server_port = int(os.getenv('WEBHOOK_PORT', 8010))
    server.run(port=server_port)
