from app.exceptions import (
    BadRequest,
    DetailedHTTPException,
    NotAuthenticated,
    PermissionDenied,
)


class AuthRequired(NotAuthenticated):
    DETAIL = "Authentication required."


class AuthorizationFailed(PermissionDenied):
    DETAIL = "Authorization failed. User has no access."


class InvalidToken(NotAuthenticated):
    DETAIL = "Invalid token."


class InvalidCredentials(PermissionDenied):
    DETAIL = "Login failed, invalid email or password"


class EmailTaken(BadRequest):
    DETAIL = "Email is already taken."


class UserNotRegistered(NotAuthenticated): ...


class RefreshTokenNotValid(NotAuthenticated):
    DETAIL = "Refresh token is not valid."


class InactiveUser(NotAuthenticated):
    DETAIL = "User is inactive"


class PasswordGenerationError(DetailedHTTPException):
    DETAIL = "A password wasn't able to be generated"
