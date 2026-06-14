from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Story Architect"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/story_architect"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:4200"]  # Angular default port

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
