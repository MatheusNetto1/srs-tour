from app.core.errors import ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    code = "user.not_found"


class UserEmailAlreadyExistsError(ConflictError):
    code = "user.email_already_exists"
