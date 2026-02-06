from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.dependencies import get_user_service
from app.models.user import (
    ActivationRequest,
    ActivationResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBasic()


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: UserRegistrationRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRegistrationResponse:
    """
    Register a new user.

    - Creates a new user account with the provided email and password
    - Sends a 4-digit activation code to the user's email
    - The activation code expires after 1 minute
    """
    return await user_service.register_user(
        email=request.email,
        password=request.password,
    )
