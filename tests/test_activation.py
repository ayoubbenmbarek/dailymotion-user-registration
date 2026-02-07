import base64

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
