from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserRegistrationResponse(BaseModel):
    """Response model for successful registration."""

    id: UUID
    email: str
    message: str = "Registration successful. Please check your email for the activation code."


class ActivationRequest(BaseModel):
    """Request model for account activation."""

    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("Activation code must be a 4-digit number")
        return v


class ActivationResponse(BaseModel):
    """Response model for successful activation."""

    message: str = "Account activated successfully"


class UserInDB(BaseModel):
    """Internal model representing a user in the database."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    activation_code: str | None = None
    activation_code_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
