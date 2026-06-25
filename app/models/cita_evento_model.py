from typing import Any

from config.database import get_cursor


class CitaEventoModel:
    """Read helpers for appointment audit events."""

    def listar_por_cita(self, id_cita: int) -> list[dict[str, Any]]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    ce.id_cita_evento,
                    ce.id_cita,
                    ce.tipo_evento,
                    ce.fecha_anterior,
                    ce.hora_anterior,
                    ce.fecha_nueva,
                    ce.hora_nueva,
                    ce.motivo,
                    ce.detalle,
                    ce.created_at,
                    CONCAT(us.nombres, ' ', us.apellidos) AS actor
                FROM cita_evento ce
                LEFT JOIN usuario_sistema us ON us.id_usuario = ce.id_usuario_actor
                WHERE ce.id_cita = %s
                ORDER BY ce.created_at DESC, ce.id_cita_evento DESC
                """,
                (id_cita,),
            )
            return cursor.fetchall()
