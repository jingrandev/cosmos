from libs.clients.llm_client.interface import ChatMessage

from .base import DialogMessage
from .base import RestaurantRole


class CustomerRole(RestaurantRole):
    @property
    def persona_messages(self) -> str:
        return """
        You are a customer at Cosmos restaurant, being served by a waiter to order food.
        You may have a certain dietary preference.
        """

    def build_context(
        self,
        extra_messages: list[ChatMessage] | None = None,
        dialog_context: list[DialogMessage] | None = None,
    ) -> list[ChatMessage]:
        if dialog_context is None:
            return super().build_context(extra_messages, dialog_context)
        messages: list[ChatMessage] = []
        for d_msg in dialog_context:
            if d_msg["role"] == "waiter":
                messages.append(self.user(d_msg["content"]))
            elif d_msg["role"] == "customer":
                messages.append(self.assistant(d_msg["content"]))
        return [
            *messages,
            *(extra_messages or []),
        ]
