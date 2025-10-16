from typing import Any
from typing import Literal
from typing import TypedDict

from libs.clients.llm_client.interface import ChatMessage
from libs.clients.llm_client.interface import LLMClient
from libs.clients.llm_client.providers.openai_client import OpenAIClient


class DialogMessage(TypedDict):
    role: Literal["waiter", "customer"]
    content: str


class RestaurantRole:
    """Base role for restaurant conversation agents.

    Provides minimal helpers to construct chat messages and perform
    non-streaming chat completions through a pluggable LLM client.
    """

    def __init__(
        self,
        *,
        client: LLMClient | None = None,
        model: str = "gpt-4o",
        temperature: float | None = None,
    ) -> None:
        self._client = client or OpenAIClient()
        self._model = model
        self._temperature = temperature

    @classmethod
    def system(cls, content: str) -> ChatMessage:
        return {"role": "system", "content": content}

    @classmethod
    def user(cls, content: str) -> ChatMessage:
        return {"role": "user", "content": content}

    @classmethod
    def assistant(cls, content: str) -> ChatMessage:
        return {"role": "assistant", "content": content}

    @classmethod
    def developer(cls, content: str) -> ChatMessage:
        return {"role": "developer", "content": content}

    @property
    def persona_messages(self) -> str:
        return ""

    def build_context(
        self,
        extra_messages: list[ChatMessage] = None,
        dialog_context: list[DialogMessage] = None,
    ) -> list[ChatMessage]:
        if extra_messages is None:
            return []
        return [*extra_messages]

    def build_messages(
        self,
        system_prompt: str,
        extra_messages: list[ChatMessage] = None,
        dialog_context: list[DialogMessage] = None,
    ) -> list[ChatMessage]:
        return [
            self.system(system_prompt),
            *self.build_context(extra_messages, dialog_context),
        ]

    def chat(
        self,
        *,
        messages: list[ChatMessage],
        temperature: float | None = None,
        response_format: str | None = None,
        extra: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> str:
        result = self._client.chat(
            model=model or self._model,
            messages=messages,
            temperature=self._temperature if temperature is None else temperature,
            response_format=response_format,  # "json" or None
            extra=extra,
        )
        return result["content"]
