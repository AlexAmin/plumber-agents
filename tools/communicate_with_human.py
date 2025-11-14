"""
Tool for agents to send WhatsApp messages to technicians or office staff.
This tool is intended to be used with an orchestrator that has WhatsApp capabilities.
"""
from typing import List, Dict, Optional, Callable

from google.genai.types import Content, Part

from shared.users import get_whatsapp_numbers_for_role
from shared.whatsapp_client import WhatsAppClient


def make_communicate_with_human_tool(message_callback: Callable[[str, Content], None] | None):
    def communicate_with_human(
            recipient_role: str,
            message: str,
            buttons: Optional[List[Dict[str, str]]] = None
    ) -> dict:
        """
        Send a WhatsApp message to a technician or office staff member.

        Use this when you need to communicate or request information from a human.

        Args:
            recipient_role: Who to send the message to. Options: "technician", "office"
            message: The message to send via WhatsApp
            buttons: Optional interactive buttons for the message
                    Example: [{"id": "yes", "title": "Yes"}, {"id": "no", "title": "No"}]

        Returns:
            dict: Status of the message sending
        """
        print(f"\n{'=' * 60}")
        print(f"📱 WHATSAPP MESSAGE")
        print(f"{'=' * 60}")
        print(f"To: {recipient_role.upper()}")
        print(f"Message: {message}")
        if buttons:
            print(f"Buttons: {[btn['title'] for btn in buttons]}")
        print(f"{'=' * 60}\n")
        whatsapp_client = WhatsAppClient()

        # Keep the chat history consistent
        if message_callback is not None:
            print("save", recipient_role, message)
            message_callback(recipient_role, Content(role="model", parts=[Part(text=message)]))

        try:
            for phone_number in get_whatsapp_numbers_for_role(recipient_role):
                whatsapp_client.send(phone_number, message, buttons=buttons)
                return {
                    "status": "sent",
                    "recipient": recipient_role,
                    "message": message,
                    "note": "Message sent via WhatsApp. Response will arrive through the normal input loop."
                }
        except:
            return {
                "status": "failed",
                "recipient": recipient_role,
                "message": message,
                "note": "Failed to send WhatsApp message. Check logs for details."
            }
    return communicate_with_human