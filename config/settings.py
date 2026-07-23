import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _is_production() -> bool:
    environment = os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    return environment.strip().lower() == "production"


def _get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        return secret_key

    if _is_production():
        raise RuntimeError("SECRET_KEY es obligatoria en entorno production")

    return "dev-secret-key-change-me"


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("MYSQL_HOST", "localhost")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "")
    database: str = os.getenv("MYSQL_DATABASE", "gestion_citas_medicas")
    charset: str = "utf8mb4"
    collation: str = "utf8mb4_unicode_ci"


class Config:
    SECRET_KEY = _get_secret_key()
    DATABASE = DatabaseConfig()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", "3600"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _is_production()
