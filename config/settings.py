import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _int_env(nombre: str, default: int) -> int:
    try:
        return int(os.getenv(nombre, str(default)) or default)
    except (TypeError, ValueError):
        return default


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
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    DATABASE = DatabaseConfig()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = _int_env("SMTP_PORT", 587)
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
    SMTP_FROM = os.getenv("SMTP_FROM", "")
