from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://postgres:postgres@db:5432/dailymotion"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    debug: bool = True

    # Activation code expiration in seconds (1 minute)
    activation_code_expiry_seconds: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
