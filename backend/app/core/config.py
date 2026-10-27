from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SRS Tour API"
    app_version: str = "0.1.0"

    database_url: str
    test_database_url: str | None = None

    app_env: str = "production"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    admin_email: str | None = None
    admin_password: str | None = None

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        weak_secret = (
            not self.secret_key.strip()
            or self.secret_key == "change-me"
            or len(self.secret_key) < 32
        )

        if self.app_env != "dev" and weak_secret:
            raise ValueError(
                "SECRET_KEY deve ter pelo menos 32 caracteres fora do ambiente dev."
            )

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
