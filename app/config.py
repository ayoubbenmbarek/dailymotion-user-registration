from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = "postgresql://postgres:postgres@db:5432/dailymotion"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    debug: bool = True

    # Activation code expiration in seconds (1 minute)
    activation_code_expiry_seconds: int = 60


settings = Settings()
