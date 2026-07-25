import os
from dataclasses import dataclass

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_ENV_PATH = os.path.join(BASE_DIR, ".env")
CONFIG_ENV_PATH = os.path.join(BASE_DIR, "config", ".env")

load_dotenv(ROOT_ENV_PATH)
load_dotenv(CONFIG_ENV_PATH, override=True)

def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default

    normalized_value = value.strip().lower()
    return normalized_value in {"1", "true", "t", "yes", "y", "on", "si", "sí"}


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
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp").strip().lower()
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USE_TLS = _get_bool_env("SMTP_USE_TLS", True)
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USER
    BREVO_API_URL = os.getenv("BREVO_API_URL", "https://api.brevo.com/v3/smtp/email")
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    BREVO_FROM_EMAIL = os.getenv("BREVO_FROM_EMAIL") or SMTP_FROM
    BREVO_FROM_NAME = os.getenv("BREVO_FROM_NAME", "Clínica Universitaria de Comas")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _is_production()
