from contextlib import contextmanager
from typing import Iterator

import mysql.connector
from mysql.connector import MySQLConnection

from config.settings import Config


def get_connection() -> MySQLConnection:
    """Devuelve una conexión MySQL configurada desde variables de entorno."""
    database_config = Config.DATABASE
    return mysql.connector.connect(
        host=database_config.host,
        port=database_config.port,
        user=database_config.user,
        password=database_config.password,
        database=database_config.database,
        charset=database_config.charset,
        collation=database_config.collation,
        autocommit=False,
    )


@contextmanager
def get_cursor(dictionary: bool = True) -> Iterator[tuple[MySQLConnection, mysql.connector.cursor.MySQLCursor]]:
    """Abre conexión/cursor y garantiza cierre seguro de recursos."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield connection, cursor
    finally:
        cursor.close()
        connection.close()


@contextmanager
def transaction(dictionary: bool = True) -> Iterator[mysql.connector.cursor.MySQLCursor]:
    """Ejecuta operaciones dentro de una transacción con commit/rollback."""
    with get_cursor(dictionary=dictionary) as (connection, cursor):
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
