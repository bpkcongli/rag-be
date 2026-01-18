from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from `.env` if present, but still allow OS env vars to override.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "rag-backend"
    app_env: str = "local"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "rag_backend"

    storage_dir: str = "/Python/rag-pipeline/storage"

    # Pluggable ML components (can be overridden via .env)
    embedding_model_name: str = "intfloat/multilingual-e5-base"

    @property
    def sqlalchemy_database_uri(self) -> str:
        # Use PyMySQL driver
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


