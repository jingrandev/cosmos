from __future__ import annotations

import os
from typing import Any

from openai import APIConnectionError
from openai import APIError
from openai import APITimeoutError
from openai import AuthenticationError
from openai import BadRequestError
from openai import OpenAI
from openai import OpenAIError
from openai import RateLimitError

from libs.clients.llm_client.exceptions import LLMClientError
from libs.clients.llm_client.exceptions import LLMHTTPError
from libs.clients.llm_client.exceptions import LLMInvalidResponseError
from libs.clients.llm_client.interface import ChatMessage
from libs.clients.llm_client.interface import ChatResult
from libs.clients.llm_client.interface import LLMClient


class OpenAIClient(LLMClient):
    """Minimal OpenAI adapter implementing the LLMClient protocol.

    - Uses SDK (openai>=2.x) to perform chat.completions.create
    - Normalizes response to ChatResult
    - Maps provider exceptions to project-level errors
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        # Fallback to environment variables when not provided
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # Instantiate OpenAI client; SDK will raise if api_key missing when required
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self._default_model = default_model

    def chat(  # type: ignore[override]
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        response_format: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ChatResult:
        # Prepare parameters for OpenAI SDK
        payload: dict[str, Any] = {
            "model": model or self._default_model,
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        if extra:
            payload.update(extra)

        try:
            resp = self._client.chat.completions.create(**payload)
        except (APITimeoutError, APIConnectionError, RateLimitError, APIError) as e:
            # Transport / server side issues
            raise LLMHTTPError(str(e)) from e
        except (BadRequestError, AuthenticationError) as e:
            # Client side configuration/params issue
            raise LLMClientError(str(e)) from e
        except OpenAIError as e:
            # Any other provider-specific error
            raise LLMInvalidResponseError(str(e)) from e
        except Exception as e:  # Safety net
            raise LLMClientError(str(e)) from e

        # Extract first choice content safely
        content = ""
        finish_reason: str | None = None
        try:
            first_choice = resp.choices[0]
            content = (
                getattr(getattr(first_choice, "message", object()), "content", "") or ""
            )
            finish_reason = getattr(first_choice, "finish_reason", None)
        except Exception:
            raise LLMInvalidResponseError(
                "missing choices[0].message.content"
            ) from None

        # Usage metrics
        usage_obj = getattr(resp, "usage", None)
        usage: dict[str, Any] | None = None
        if usage_obj is not None:
            try:
                if hasattr(usage_obj, "model_dump"):
                    usage = usage_obj.model_dump()
                elif hasattr(usage_obj, "to_dict"):
                    usage = usage_obj.to_dict()
                else:
                    usage = {
                        k: getattr(usage_obj, k)
                        for k in ("prompt_tokens", "completion_tokens", "total_tokens")
                        if hasattr(usage_obj, k)
                    }
            except Exception:
                usage = None

        model_id = getattr(resp, "model", model)
        try:
            raw_min = {"id": getattr(resp, "id", None)}
        except Exception:
            raw_min = None

        return ChatResult(
            content=content,
            model=model_id,
            finish_reason=finish_reason,
            usage=usage,
            raw=raw_min,
        )
