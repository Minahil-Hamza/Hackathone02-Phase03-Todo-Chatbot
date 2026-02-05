"""Custom exceptions for authentication and authorization."""

from typing import Optional


class AuthException(Exception):
    """Base exception for authentication errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 401,
        headers: Optional[dict] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.headers = headers or {}
        super().__init__(message)


class InvalidCredentialsError(AuthException):
    """Raised when email or password is incorrect."""

    def __init__(self):
        super().__init__(
            code="INVALID_CREDENTIALS",
            message="Email or password is incorrect",
            status_code=401,
        )


class TokenExpiredError(AuthException):
    """Raised when a token has expired."""

    def __init__(self, token_type: str = "Token"):
        super().__init__(
            code="TOKEN_EXPIRED",
            message=f"{token_type} has expired",
            status_code=401,
        )


class TokenRevokedError(AuthException):
    """Raised when a token has been revoked."""

    def __init__(self):
        super().__init__(
            code="TOKEN_REVOKED",
            message="Token has been revoked",
            status_code=401,
        )


class InvalidTokenError(AuthException):
    """Raised when a token is invalid or malformed."""

    def __init__(self, message: str = "Invalid or malformed token"):
        super().__init__(
            code="INVALID_TOKEN",
            message=message,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class EmailExistsError(AuthException):
    """Raised when attempting to register with an existing email."""

    def __init__(self):
        super().__init__(
            code="EMAIL_EXISTS",
            message="Email is already registered",
            status_code=400,
        )


class AccountDisabledError(AuthException):
    """Raised when a user's account is disabled."""

    def __init__(self):
        super().__init__(
            code="ACCOUNT_DISABLED",
            message="User account is disabled",
            status_code=401,
        )
