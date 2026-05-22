from typing import Any

from config.database import get_cursor, transaction


class HorarioModel:
    """Modelo de disponibilidad horaria de médicos."""

    def listar_por_medico(self, id_medico: int) -> list[dict[str, Any]]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    id_horario,
                    id_medico,
                    fecha,
                    hora_inicio,
                    hora_fin,
                    estado
                FROM horario
                WHERE id_medico = %s
                ORDER BY fecha ASC, hora_inicio ASC
                """,
                (id_medico,),
            )
            return cursor.fetchall()

    def crear(self, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO horario (
                    id_medico,
                    fecha,
                    hora_inicio,
                    hora_fin,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    datos["id_medico"],
                    datos["fecha"],
                    datos["hora_inicio"],
                    datos["hora_fin"],
                    datos["estado"],
                ),
            )
            return int(cursor.lastrowid)

    def actualizar_estado(self, id_horario: int, estado: str) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                UPDATE horario
                SET estado = %s
                WHERE id_horario = %s
                """,
                (estado, id_horario),
            )
