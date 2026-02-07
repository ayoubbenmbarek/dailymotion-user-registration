import base64
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.conftest import MockEmailService, MockUserRepository


def basic_auth_header(email: str, password: str) -> dict:
    """Create Basic Auth header."""
    credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.mark.asyncio
async def test_activate_user_success(
    client: AsyncClient,
    mock_repository: MockUserRepository,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test successful user activation."""
    await client.post("/users/register", json=valid_user_data)

    code = mock_email_service.sent_emails[0]["code"]

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Account activated successfully"

    user = await mock_repository.get_user_by_email(valid_user_data["email"])
    assert user is not None
    assert user.is_active is True
    assert user.activation_code is None


@pytest.mark.asyncio
async def test_activate_user_wrong_code(
    client: AsyncClient,
    valid_user_data: dict,
):
    """Test activation with wrong code fails."""
    await client.post("/users/register", json=valid_user_data)

    response = await client.post(
        "/users/activate",
        json={"code": "0000"},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 400
    assert "Invalid activation code" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_user_expired_code(
    client: AsyncClient,
    mock_repository: MockUserRepository,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test activation with expired code fails."""
    await client.post("/users/register", json=valid_user_data)

    code = mock_email_service.sent_emails[0]["code"]

    user = await mock_repository.get_user_by_email(valid_user_data["email"])
    assert user is not None
    expired_time = datetime.now(UTC) - timedelta(minutes=5)
    await mock_repository.update_activation_code(user.id, code, expired_time)

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_activate_user_invalid_credentials(
    client: AsyncClient,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test activation with invalid credentials fails."""
    await client.post("/users/register", json=valid_user_data)
    code = mock_email_service.sent_emails[0]["code"]

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header(valid_user_data["email"], "WrongPassword123"),
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_user_nonexistent_user(client: AsyncClient):
    """Test activation for non-existent user fails."""
    response = await client.post(
        "/users/activate",
        json={"code": "1234"},
        headers=basic_auth_header("nonexistent@example.com", "SomePassword123"),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_activate_user_no_auth(client: AsyncClient):
    """Test activation without auth header fails."""
    response = await client.post(
        "/users/activate",
        json={"code": "1234"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_activate_user_already_active(
    client: AsyncClient,
    mock_email_service: MockEmailService,
    valid_user_data: dict,
):
    """Test activation of already active user fails."""
    await client.post("/users/register", json=valid_user_data)
    code = mock_email_service.sent_emails[0]["code"]

    await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    response = await client.post(
        "/users/activate",
        json={"code": "1234"},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 400
    assert "already activated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_user_invalid_code_format(
    client: AsyncClient,
    valid_user_data: dict,
):
    """Test activation with invalid code format fails."""
    await client.post("/users/register", json=valid_user_data)

    response = await client.post(
        "/users/activate",
        json={"code": "abcd"},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_activate_user_code_too_short(
    client: AsyncClient,
    valid_user_data: dict,
):
    """Test activation with code that's too short fails."""
    await client.post("/users/register", json=valid_user_data)

    response = await client.post(
        "/users/activate",
        json={"code": "123"},
        headers=basic_auth_header(valid_user_data["email"], valid_user_data["password"]),
    )

    assert response.status_code == 422
