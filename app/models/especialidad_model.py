from typing import Any

from config.database import get_cursor, transaction


class EspecialidadModel:
    """Modelo de catálogo de especialidades médicas."""

    def listar(self) -> list[dict[str, Any]]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    e.id_especialidad,
                    e.nombre,
                    e.descripcion
                FROM especialidad e
                ORDER BY e.nombre ASC
                """
            )
            return cursor.fetchall()

    def listar_con_total_medicos(self) -> list[dict[str, Any]]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    e.id_especialidad,
                    e.nombre,
                    e.descripcion,
                    COUNT(m.id_medico) AS medicos
                FROM especialidad e
                LEFT JOIN medico m ON m.id_especialidad = e.id_especialidad
                GROUP BY e.id_especialidad, e.nombre, e.descripcion
                ORDER BY e.nombre ASC
                """
            )
            return cursor.fetchall()

    def crear(self, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO especialidad (nombre, descripcion)
                VALUES (%s, %s)
                """,
                (
                    datos["nombre"],
                    datos.get("descripcion"),
                ),
            )
            return int(cursor.lastrowid)
