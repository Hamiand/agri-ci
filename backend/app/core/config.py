from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AGRI-CI"
    app_env: str = "development"
    app_debug: bool = False
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 30
    jwt_refresh_token_days: int = 30
    api_v1_prefix: str = "/api/v1"
    # Keep the environment representation scalar. Pydantic-settings attempts
    # JSON decoding for list fields before field validators run, while our
    # deployment contract intentionally uses a comma-separated CORS_ORIGINS.
    cors_origins: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
