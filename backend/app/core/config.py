from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central place for every environment-driven value the backend needs.
    Reads from a `.env` file in the backend/ directory (or real
    environment variables in production) — nothing here is ever
    hard-coded, per docs/06-security-and-privacy.md.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    jwt_expiry_minutes: int = 60

    ai_provider: str = "mock"
    ai_provider_api_key: str = ""

    storage_backend: str = "local"

    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"


settings = Settings()
