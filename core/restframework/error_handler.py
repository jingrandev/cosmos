from typing import Any

from django.utils.translation import gettext_lazy as _

error_registry: dict[int, type] = {}


class BaseError(Exception):
    """Base class for API errors.

    This class serves as a base for all API-specific exceptions. Do not use this class directly;
    instead, create a subclass for each specific error type.

    Attributes:
        code (int): Error code. Reserved codes (1-19) are for system use.
            Subclass codes should start from 20 and increment.
        message (str): Default error message.

    Note:
        - Each specific error type that needs to be handled by the frontend should have its own subclass
          with a unique error code.
        - For request parameter validation errors, use HTTP 400 responses directly instead of this class.
        - The error registry ensures unique error codes across all subclasses.
    """

    code: int = 1
    message: str = _("API Internal Error")

    def __init__(self, message: str | None = None) -> None:
        """Initialize the error with an optional custom message.

        Args:
            message: Custom error message. If None, uses the class default message.
        """
        super().__init__(message or self.message)
        self.message = message or self.message

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register subclass error codes in the global registry.

        Raises:
            ValueError: If the error code is already registered.
        """
        if cls.code in error_registry:
            error_msg = f"Error code {cls.code} is already registered by {error_registry[cls.code].__name__}"
            raise ValueError(error_msg)
        error_registry[cls.code] = cls
        super().__init_subclass__(**kwargs)

    def __str__(self) -> str:
        return self.message

    def get_response_data(self) -> dict[str, list[dict[str, Any]]]:
        """Get the error response data in a standardized format.

        Returns:
            A dictionary containing the error code and message in the standard format.
        """
        return {"errors": [{"code": self.code, "message": self.message}]}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(code={self.code}, message={self.message!r})>"
