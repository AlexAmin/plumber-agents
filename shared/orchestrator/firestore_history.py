"""
Firestore-based chat history persistence for the orchestrator.
Stores and retrieves conversation history by user ID.
"""

import os
from typing import List, Dict

import firebase_admin
from firebase_admin import firestore
from google.genai.types import Content, Part


class FirestoreHistory:
    """Manages chat history persistence in Firestore."""

    def __init__(self, collection_name: str = "chat_history"):
        """
        Initialize Firestore client.

        Args:
            collection_name: Firestore collection to use for chat history
        """
        self.app = firebase_admin.initialize_app()
        self.db = firestore.client()
        self.collection = collection_name

    def load_history(self, user_id: str) -> List[Content]:
        """
        Load chat history for a user from Firestore.

        Args:
            user_id: User identifier

        Returns:
            List of Content objects representing chat history
        """
        doc_ref = self.db.collection(self.collection).document(user_id)
        doc = doc_ref.get()

        if not doc.exists:
            return []

        data = doc.to_dict()
        messages = data.get("messages", [])

        # Convert stored dicts back to Content objects
        history = []
        for msg in messages:
            parts = [Part(text=part["text"]) for part in msg.get("parts", [])]
            history.append(Content(role=msg["role"], parts=parts))

        return history

    def save_history(self, user_id: str, history: List[Content]) -> None:
        # Convert Content objects to serializable dicts
        messages = []
        for content in history:
            messages.append({
                "role": content.role,
                "parts": [{"text": part.text} for part in content.parts if hasattr(part, "text")]
            })
        doc_ref = self.db.collection(self.collection).document(user_id)
        doc_ref.set({
            "messages": messages,
            "updated_at": firestore.firestore.SERVER_TIMESTAMP
        })

    def append_message(self, user_id: str, content: Content) -> None:
        """
        Append a single message to user's chat history.

        Args:
            user_id: User identifier
            content: Content object to append
        """
        message = {
            "role": content.role,
            "parts": [{"text": part.text} for part in content.parts if hasattr(part, "text")]
        }

        doc_ref = self.db.collection(self.collection).document(user_id)
        doc_ref.update({
            "messages": firestore.ArrayUnion([message]),
            "updated_at": firestore.SERVER_TIMESTAMP
        })

    def clear_history(self, user_id: str) -> None:
        """
        Clear chat history for a user.

        Args:
            user_id: User identifier
        """
        doc_ref = self.db.collection(self.collection).document(user_id)
        doc_ref.delete()

    def load_all_histories(self) -> Dict[str, List[Content]]:
        """
        Load chat histories for all users.

        Returns:
            Dictionary mapping user_id to chat history
        """
        all_histories = {}
        docs = self.db.collection(self.collection).stream()

        for doc in docs:
            user_id = doc.id
            all_histories[user_id] = self.load_history(user_id)

        return all_histories
