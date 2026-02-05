from datetime import datetime
from typing import Optional
from uuid import UUID

import asyncpg

from app.models.user import UserInDB


class UserRepository:
    """Data access layer for user operations using raw SQL."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_user(
        self,
        email: str,
        password_hash: str,
        activation_code: str,
        activation_code_expires_at: datetime,
    ) -> UserInDB:
        """Create a new user in the database."""
        query = """
            INSERT INTO users (email, password_hash, activation_code, activation_code_expires_at)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, password_hash, is_active, activation_code,
                      activation_code_expires_at, created_at, updated_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query, email, password_hash, activation_code, activation_code_expires_at
            )
            return UserInDB(**dict(row))

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Retrieve a user by email address."""
        query = """
            SELECT id, email, password_hash, is_active, activation_code,
                   activation_code_expires_at, created_at, updated_at
            FROM users
            WHERE email = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, email)
            if row:
                return UserInDB(**dict(row))
            return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserInDB]:
        """Retrieve a user by ID."""
        query = """
            SELECT id, email, password_hash, is_active, activation_code,
                   activation_code_expires_at, created_at, updated_at
            FROM users
            WHERE id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            if row:
                return UserInDB(**dict(row))
            return None

    async def activate_user(self, user_id: UUID) -> bool:
        """Activate a user account and clear the activation code."""
        query = """
            UPDATE users
            SET is_active = TRUE,
                activation_code = NULL,
                activation_code_expires_at = NULL,
                updated_at = NOW()
            WHERE id = $1
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(query, user_id)
            return result is not None

    async def update_activation_code(
        self,
        user_id: UUID,
        activation_code: str,
        activation_code_expires_at: datetime,
    ) -> bool:
        """Update the activation code for a user."""
        query = """
            UPDATE users
            SET activation_code = $2,
                activation_code_expires_at = $3,
                updated_at = NOW()
            WHERE id = $1
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                query, user_id, activation_code, activation_code_expires_at
            )
            return result is not None

    async def email_exists(self, email: str) -> bool:
        """Check if an email already exists in the database."""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, email)
