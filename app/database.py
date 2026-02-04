import asyncpg
from typing import Optional

from app.config import settings


class Database:
    """Manages asyncpg connection pool."""

    pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def connect(cls) -> None:
        """Create the database connection pool."""
        cls.pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=5,
            max_size=20,
        )

    @classmethod
    async def disconnect(cls) -> None:
        """Close the database connection pool."""
        if cls.pool:
            await cls.pool.close()
            cls.pool = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Get the connection pool, ensuring it exists."""
        if cls.pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return cls.pool
