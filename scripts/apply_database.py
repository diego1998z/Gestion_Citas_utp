from __future__ import annotations

import sys
from pathlib import Path

import mysql.connector
from mysql.connector import Error as MySQLError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import Config  # noqa: E402


SQL_FILES = (
    PROJECT_ROOT / "database" / "schema.sql",
    PROJECT_ROOT / "database" / "migrations" / "20260625_appointment_workflow.sql",
    PROJECT_ROOT / "database" / "seed.sql",
)

SAFE_ALTER_ERRNOS = {1060, 1061, 1091, 1826}


def main() -> int:
    database_config = Config.DATABASE
    connection = mysql.connector.connect(
        host=database_config.host,
        port=database_config.port,
        user=database_config.user,
        password=database_config.password,
        database=database_config.database,
        charset=database_config.charset,
        collation=database_config.collation,
        autocommit=False,
    )

    try:
        cursor = connection.cursor()
        try:
            for sql_file in SQL_FILES:
                print(f"Applying {sql_file.relative_to(PROJECT_ROOT)}...")
                for statement in _load_statements(sql_file):
                    _execute_statement(cursor, statement)
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()

    print("Database setup completed.")
    return 0


def _load_statements(sql_file: Path) -> list[str]:
    sql = sql_file.read_text(encoding="utf-8")
    return [statement for statement in _split_sql(sql) if not _should_skip(statement)]


def _execute_statement(cursor, statement: str) -> None:
    try:
        cursor.execute(statement)
    except MySQLError as error:
        if _is_safe_idempotent_error(error, statement):
            print(f"Skipping already-applied statement ({error.errno}).")
            return
        raise


def _should_skip(statement: str) -> bool:
    normalized = statement.strip().lower()
    return normalized.startswith("create database") or normalized.startswith("use ")


def _is_safe_idempotent_error(error: MySQLError, statement: str) -> bool:
    normalized = statement.strip().lower()
    return normalized.startswith("alter table") and getattr(error, "errno", None) in SAFE_ALTER_ERRNOS


def _split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    in_line_comment = False
    in_block_comment = False
    i = 0

    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                current.append(char)
            i += 1
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if quote is None and char == "-" and next_char == "-":
            in_line_comment = True
            i += 2
            continue

        if quote is None and char == "#":
            in_line_comment = True
            i += 1
            continue

        if quote is None and char == "/" and next_char == "*":
            in_block_comment = True
            i += 2
            continue

        current.append(char)

        if char in {"'", '"', "`"}:
            if quote is None:
                quote = char
            elif quote == char and not _is_escaped(sql, i):
                quote = None
        elif char == ";" and quote is None:
            statement = "".join(current[:-1]).strip()
            if statement:
                statements.append(statement)
            current = []

        i += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def _is_escaped(sql: str, index: int) -> bool:
    backslashes = 0
    i = index - 1
    while i >= 0 and sql[i] == "\\":
        backslashes += 1
        i -= 1
    return backslashes % 2 == 1


if __name__ == "__main__":
    raise SystemExit(main())
