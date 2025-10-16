from core.restframework.error_handler import BaseError


class LLMClientError(BaseError):
    code: int = 20
    message: str = "LLM client error"


class LLMHTTPError(BaseError):
    code: int = 21
    message: str = "LLM HTTP error"


class LLMInvalidResponseError(BaseError):
    code: int = 22
    message: str = "LLM invalid response"
