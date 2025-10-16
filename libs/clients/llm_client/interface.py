from typing import Any
from typing import Literal
from typing import Protocol
from typing import TypedDict


class ChatMessage(TypedDict):
    """Minimal chat message structure compatible with common LLM providers."""

    role: Literal["system", "user", "assistant", "developer"]
    content: str


class ChatResult(TypedDict, total=False):
    """Normalized result for a single-turn chat completion."""

    content: str
    model: str
    finish_reason: str | None
    usage: dict[str, Any] | None
    raw: dict[str, Any] | None


class LLMClient(Protocol):
    """Protocol for LLM clients.

    Implementations should perform the HTTP request to an LLM provider,
    normalize the response into ChatResult, and raise defined errors when needed.
    """

    def chat(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        response_format: Literal["text", "json"] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ChatResult:
        """Create a non-streaming chat completion.

        Returns:
            ChatResult: normalized completion result with primary text content.

        Raises:
            LLMClientError: for client-side validation or configuration issues.
            LLMHTTPError: for transport errors (timeouts, non-2xx, etc.).
            LLMInvalidResponseError: when the provider returns malformed data.
        """
        ...
