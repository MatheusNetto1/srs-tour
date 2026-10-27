from app.core.errors import ForbiddenError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    code = "auth.invalid_credentials"


class InvalidTokenError(UnauthorizedError):
    code = "auth.invalid_token"


class TokenExpiredError(UnauthorizedError):
    code = "auth.token_expired"


class AuthForbiddenError(ForbiddenError):
    code = "auth.forbidden"
