from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_email_service, get_user_repository
from app.main import app
from app.models.user import UserInDB
from app.services.email_service import EmailServiceInterface


class MockUserRepository:
    """Mock repository for testing without database."""

    def __init__(self):
        self.users: dict[str, UserInDB] = {}

    async def create_user(
        self,
        email: str,
        password_hash: str,
        activation_code: str,
        activation_code_expires_at: datetime,
    ) -> UserInDB:
        user = UserInDB(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            is_active=False,
            activation_code=activation_code,
            activation_code_expires_at=activation_code_expires_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.users[email] = user
        return user

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        return self.users.get(email)

    async def get_user_by_id(self, user_id) -> UserInDB | None:
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    async def activate_user(self, user_id) -> bool:
        for email, user in self.users.items():
            if user.id == user_id:
                self.users[email] = user.model_copy(
                    update={
                        "is_active": True,
                        "activation_code": None,
                        "activation_code_expires_at": None,
                    }
                )
                return True
        return False

    async def update_activation_code(
        self, user_id, activation_code: str, activation_code_expires_at: datetime
    ) -> bool:
        for email, user in self.users.items():
            if user.id == user_id:
                self.users[email] = user.model_copy(
                    update={
                        "activation_code": activation_code,
                        "activation_code_expires_at": activation_code_expires_at,
                    }
                )
                return True
        return False

    async def email_exists(self, email: str) -> bool:
        return email in self.users


class MockEmailService(EmailServiceInterface):
    """Mock email service for testing."""

    def __init__(self):
        self.sent_emails: list[dict] = []

    async def send_activation_code(self, email: str, code: str) -> bool:
        self.sent_emails.append({"email": email, "code": code})
        return True


@pytest.fixture
def mock_repository() -> MockUserRepository:
    """Create a mock repository instance."""
    return MockUserRepository()


@pytest.fixture
def mock_email_service() -> MockEmailService:
    """Create a mock email service instance."""
    return MockEmailService()


@pytest_asyncio.fixture
async def client(
    mock_repository: MockUserRepository,
    mock_email_service: MockEmailService,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with mocked dependencies."""

    async def override_get_repository():
        return mock_repository

    async def override_get_email_service():
        return mock_email_service

    app.dependency_overrides[get_user_repository] = override_get_repository
    app.dependency_overrides[get_email_service] = override_get_email_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def valid_user_data() -> dict:
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123",
    }


@pytest.fixture
def weak_password_data() -> dict:
    """User data with weak password."""
    return {
        "email": "test@example.com",
        "password": "short",
    }


@pytest.fixture
def invalid_email_data() -> dict:
    """User data with invalid email."""
    return {
        "email": "not-an-email",
        "password": "SecurePass123",
    }
