from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class CustomException(HTTPException):
    """Base class for all custom exceptions."""

    def __init__(
            self,
            status_code: int,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(CustomException):
    """Exception raised when a resource is not found."""

    def __init__(
            self,
            detail: Any = "Resource not found",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class UnauthorizedException(CustomException):
    """Exception raised when a user is not authorized."""

    def __init__(
            self,
            detail: Any = "Not authenticated",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"} if headers is None else headers,
        )


class ForbiddenException(CustomException):
    """Exception raised when a user is forbidden from accessing a resource."""

    def __init__(
            self,
            detail: Any = "Access forbidden",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class BadRequestException(CustomException):
    """Exception raised when a request is malformed."""

    def __init__(
            self,
            detail: Any = "Bad request",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
        )


class ConflictException(CustomException):
    """Exception raised when there is a conflict in the request."""

    def __init__(
            self,
            detail: Any = "Conflict",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers,
        )


class PaymentRequiredException(CustomException):
    """Exception raised when payment is required."""

    def __init__(
            self,
            detail: Any = "Payment required",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            headers=headers,
        )


class UnprocessableEntityException(CustomException):
    """Exception raised when an entity cannot be processed."""

    def __init__(
            self,
            detail: Any = "Unprocessable entity",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )


class ServiceUnavailableException(CustomException):
    """Exception raised when a service is unavailable."""

    def __init__(
            self,
            detail: Any = "Service unavailable",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )


class InternalServerException(CustomException):
    """Exception raised when there is an internal server error."""

    def __init__(
            self,
            detail: Any = "Internal server error",
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )
