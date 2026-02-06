import secrets
from datetime import datetime, timedelta, timezone

from passlib.hash import bcrypt

from app.config import settings
from app.exceptions import (
    ActivationCodeExpiredError,
    InvalidActivationCodeError,
    InvalidCredentialsError,
    UserAlreadyActiveError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.user import UserInDB, UserRegistrationResponse
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailServiceInterface


class UserService:
    """Business logic layer for user operations."""

    def __init__(self, repository: UserRepository, email_service: EmailServiceInterface):
        self.repository = repository
        self.email_service = email_service

    @staticmethod
    def generate_activation_code() -> str:
        """Generate a cryptographically secure 4-digit activation code."""
        return f"{secrets.randbelow(10000):04d}"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.verify(password, password_hash)

    async def register_user(self, email: str, password: str) -> UserRegistrationResponse:
        """Register a new user and send activation code."""
        if await self.repository.email_exists(email):
            raise UserAlreadyExistsError()

        activation_code = self.generate_activation_code()
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.activation_code_expiry_seconds
        )

        password_hash = self.hash_password(password)
        user = await self.repository.create_user(
            email=email,
            password_hash=password_hash,
            activation_code=activation_code,
            activation_code_expires_at=expires_at,
        )

        await self.email_service.send_activation_code(email, activation_code)

        return UserRegistrationResponse(id=user.id, email=user.email)

    async def authenticate_user(self, email: str, password: str) -> UserInDB:
        """Authenticate a user by email and password."""
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        return user

    async def activate_user(self, email: str, password: str, code: str) -> bool:
        """Activate a user account with the provided code."""
        user = await self.authenticate_user(email, password)

        if user.is_active:
            raise UserAlreadyActiveError()

        if user.activation_code != code:
            raise InvalidActivationCodeError()

        if user.activation_code_expires_at is None:
            raise InvalidActivationCodeError()

        now = datetime.now(timezone.utc)
        expires_at = user.activation_code_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now > expires_at:
            raise ActivationCodeExpiredError()

        return await self.repository.activate_user(user.id)

    async def resend_activation_code(self, email: str, password: str) -> bool:
        """Generate and send a new activation code."""
        user = await self.authenticate_user(email, password)

        if user.is_active:
            raise UserAlreadyActiveError()

        activation_code = self.generate_activation_code()
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.activation_code_expiry_seconds
        )

        await self.repository.update_activation_code(
            user.id, activation_code, expires_at
        )
        await self.email_service.send_activation_code(email, activation_code)

        return True
