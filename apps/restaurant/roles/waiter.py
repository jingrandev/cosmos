from libs.clients.llm_client.interface import ChatMessage

from .base import DialogMessage
from .base import RestaurantRole


class WaiterRole(RestaurantRole):
    @property
    def persona_messages(self) -> str:
        return """
        You are a friendly and passionate waiter at Cosmos Restaurant.
        Your tone is warm, professional, and approachable.
        """

    def build_context(
        self,
        extra_messages: list[ChatMessage] = None,
        dialog_context: list[DialogMessage] = None,
    ) -> list[ChatMessage]:
        if dialog_context is None:
            return super().build_context(extra_messages, dialog_context)
        messages = []
        for d_msg in dialog_context:
            if d_msg["role"] == "customer":
                messages.append(self.user(d_msg["content"]))
            elif d_msg["role"] == "waiter":
                messages.append(self.assistant(d_msg["content"]))
        return [
            *messages,
            *extra_messages,
        ]
