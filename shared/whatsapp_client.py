"""
WhatsApp Cloud API client (Meta/Facebook official API)
Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
"""

import requests
import os
from typing import Dict, Optional, List


class WhatsAppClient:
    """
    Official WhatsApp Cloud API client for sending messages.
    Messages are received via webhook callbacks (not polling).
    """

    def __init__(self, config: Dict = None):
        """
        Initialize WhatsApp client with Meta Cloud API credentials.

        Args:
            config: Optional configuration dict. If not provided, reads from env vars.
                   Keys: access_token, phone_number_id, business_account_id, api_version
        """
        config = config or {}

        # Meta API credentials
        self.access_token = config.get('access_token') or os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = config.get('phone_number_id') or os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.business_account_id = config.get('business_account_id') or os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')

        # Validate required credentials
        if not self.access_token:
            raise ValueError("WHATSAPP_ACCESS_TOKEN is required")
        if not self.phone_number_id:
            raise ValueError("WHATSAPP_PHONE_NUMBER_ID is required")

        # API endpoints
        self.base_url = f'https://graph.facebook.com/v22.0'
        self.send_url = f'{self.base_url}/{self.phone_number_id}/messages'

    def send(self, to_number: str, message: str, buttons: Optional[List[Dict]] = None) -> Dict:

        """
        Send WhatsApp message (text or interactive with buttons).

        Args:
            to_number: Recipient phone number (format: "1234567890" without + or spaces)
            message: Message content
            buttons: Optional list of buttons for interactive message
                    Example: [{"id": "yes", "title": "Yes"}, {"id": "no", "title": "No"}]

        Returns:
            Response from WhatsApp API containing message_id and status

        Raises:
            requests.HTTPError: If API request fails
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Build payload based on whether buttons are provided
        if buttons:
            # Interactive message with buttons
            button_components = [
                {
                    "type": "reply",
                    "reply": {
                        "id": btn['id'],
                        "title": btn['title'][:20]  # WhatsApp limits button title to 20 chars
                    }
                }
                for btn in buttons[:3]  # Max 3 buttons
            ]

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {
                        "buttons": button_components
                    }
                }
            }
        else:
            # Simple text message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": message}
            }

        try:
            response = requests.post(
                self.send_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending WhatsApp message: {e} - {payload}")
            raise

    def mark_as_read(self, message_id: str) -> Dict:
        """
        Mark message as read (optional, improves UX).

        Args:
            message_id: WhatsApp message ID (wamid.xxx)

        Returns:
            Response from WhatsApp API
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }

        try:
            response = requests.post(
                self.send_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Non-critical, just log and continue
            print(f"Warning: Failed to mark message as read: {e}")
            return {}

    def get_media_url(self, media_id: str) -> Optional[str]:
        """
        Get media download URL from media ID.
        Used for downloading images, audio, documents sent by users.

        Args:
            media_id: Media ID from webhook message

        Returns:
            Download URL or None if failed
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

        try:
            response = requests.get(
                f'{self.base_url}/{media_id}',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('url')
        except requests.exceptions.RequestException as e:
            print(f"Error getting media URL: {e}")
            return None

    def download_media(self, media_url: str, output_path: str) -> bool:
        """
        Download media file from WhatsApp.

        Args:
            media_url: URL from get_media_url()
            output_path: Local file path to save media

        Returns:
            True if successful, False otherwise
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

        try:
            response = requests.get(media_url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            return True
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error downloading media: {e}")
            return False
