from typing import Annotated

from fastapi import Depends

from app.database import Database
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailServiceInterface, SMTPEmailService
from app.services.user_service import UserService


async def get_user_repository() -> UserRepository:
    """Dependency for UserRepository."""
    pool = await Database.get_pool()
    return UserRepository(pool)


async def get_email_service() -> EmailServiceInterface:
    """Dependency for EmailService."""
    return SMTPEmailService()


async def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailServiceInterface, Depends(get_email_service)],
) -> UserService:
    """Dependency for UserService."""
    return UserService(repository, email_service)
