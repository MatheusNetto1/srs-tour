from app.core.errors import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    code = "auth.invalid_credentials"


class InvalidTokenError(UnauthorizedError):
    code = "auth.invalid_token"
