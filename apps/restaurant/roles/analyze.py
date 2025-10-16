# ruff: noqa: E501
from apps.restaurant.roles.base import RestaurantRole


class AnalyzeDialogRole(RestaurantRole):
    @property
    def persona_messages(self) -> str:
        return """
        You are an assistant specialized in detecting a customer's dietary preference from conversation.
        """
