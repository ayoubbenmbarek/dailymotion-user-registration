from fastapi import HTTPException, status


class UserAlreadyExistsError(HTTPException):
    """Raised when attempting to register with an email that already exists."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


class UserNotFoundError(HTTPException):
    """Raised when a user is not found."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class InvalidCredentialsError(HTTPException):
    """Raised when authentication credentials are invalid."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


class InvalidActivationCodeError(HTTPException):
    """Raised when the activation code is invalid."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activation code",
        )


class ActivationCodeExpiredError(HTTPException):
    """Raised when the activation code has expired."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation code has expired. Please request a new one.",
        )


class UserAlreadyActiveError(HTTPException):
    """Raised when trying to activate an already active user."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already activated",
        )
