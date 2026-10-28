import pytest
from pydantic import ValidationError

from app.core.config import Settings

DATABASE_URL = "postgresql+psycopg://user:password@localhost/database"


def test_rejects_weak_secret_key_when_app_env_is_missing() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY deve ter pelo menos"):
        Settings(
            _env_file=None,
            database_url=DATABASE_URL,
            secret_key="change-me",
        )


def test_accepts_weak_secret_key_in_dev() -> None:
    settings = Settings(
        _env_file=None,
        app_env="dev",
        database_url=DATABASE_URL,
        secret_key="change-me",
    )

    assert settings.app_env == "dev"


def test_accepts_strong_secret_key_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

    settings = Settings(
        _env_file=None,
        app_env="production",
        database_url=DATABASE_URL,
        secret_key="s" * 32,
    )

    assert settings.access_token_expire_minutes == 480
