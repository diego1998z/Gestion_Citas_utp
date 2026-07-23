from typing import Any

from config.database import get_cursor, transaction


class HorarioModel:
    """Modelo de disponibilidad horaria de médicos."""

    def listar_por_medico(
        self,
        id_medico: int,
        *,
        solo_futuros: bool = False,
        solo_disponibles: bool = False,
    ) -> list[dict[str, Any]]:
        filtros = ["id_medico = %s"]
        parametros: list[Any] = [id_medico]

        if solo_futuros:
            filtros.append("fecha >= CURDATE()")

        if solo_disponibles:
            filtros.append("estado = 'DISPONIBLE'")

        where_sql = " AND ".join(filtros)

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    id_horario,
                    id_medico,
                    fecha,
                    hora_inicio,
                    hora_fin,
                    estado
                FROM horario
                WHERE {where_sql}
                ORDER BY fecha ASC, hora_inicio ASC
                """,
                tuple(parametros),
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
