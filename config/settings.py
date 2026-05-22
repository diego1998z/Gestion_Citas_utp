import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


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
