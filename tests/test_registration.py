import pytest
from httpx import AsyncClient

from tests.conftest import MockEmailService, MockUserRepository


@pytest.mark.asyncio
async def test_register_user_success(
    client: AsyncClient,
    mock_repository: MockUserRepository,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test successful user registration."""
    response = await client.post("/users/register", json=valid_user_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == valid_user_data["email"]
    assert "message" in data

    user = await mock_repository.get_user_by_email(valid_user_data["email"])
    assert user is not None
    assert user.is_active is False
    assert user.activation_code is not None

    assert len(mock_email_service.sent_emails) == 1
    assert mock_email_service.sent_emails[0]["email"] == valid_user_data["email"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email(
    client: AsyncClient,
    valid_user_data: dict,
):
    """Test registration with duplicate email fails."""
    response1 = await client.post("/users/register", json=valid_user_data)
    assert response1.status_code == 201

    response2 = await client.post("/users/register", json=valid_user_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_invalid_email(
    client: AsyncClient,
    invalid_email_data: dict,
):
    """Test registration with invalid email format fails."""
    response = await client.post("/users/register", json=invalid_email_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_weak_password(
    client: AsyncClient,
    weak_password_data: dict,
):
    """Test registration with weak password fails."""
    response = await client.post("/users/register", json=weak_password_data)
    assert response.status_code == 422
    assert "8 characters" in str(response.json())


@pytest.mark.asyncio
async def test_register_user_missing_fields(client: AsyncClient):
    """Test registration with missing fields fails."""
    response = await client.post("/users/register", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_missing_password(client: AsyncClient):
    """Test registration without password fails."""
    response = await client.post("/users/register", json={"email": "test@example.com"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_missing_email(client: AsyncClient):
    """Test registration without email fails."""
    response = await client.post("/users/register", json={"password": "SecurePass123"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_activation_code_is_4_digits(
    client: AsyncClient,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test that activation code is exactly 4 digits."""
    await client.post("/users/register", json=valid_user_data)

    code = mock_email_service.sent_emails[0]["code"]
    assert len(code) == 4
    assert code.isdigit()
