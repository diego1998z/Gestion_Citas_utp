from typing import Any

from config.database import get_cursor


class ReporteModel:
    """Consultas SQL para reportes administrativos.

    Las vistas no consultan la base de datos directamente; este modelo concentra
    el listado filtrado de citas usado por el reporte básico del MVP.
    """

    def listar_citas(self, filtros: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filtros = filtros or {}
        condiciones: list[str] = []
        parametros: list[Any] = []

        if filtros.get("estado"):
            condiciones.append("c.estado = %s")
            parametros.append(filtros["estado"])

        if filtros.get("id_medico"):
            condiciones.append("c.id_medico = %s")
            parametros.append(filtros["id_medico"])

        if filtros.get("fecha_inicio"):
            condiciones.append("c.fecha >= %s")
            parametros.append(filtros["fecha_inicio"])

        if filtros.get("fecha_fin"):
            condiciones.append("c.fecha <= %s")
            parametros.append(filtros["fecha_fin"])

        where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    c.id_cita,
                    CONCAT('CIT-', LPAD(c.id_cita, 4, '0')) AS codigo,
                    c.fecha,
                    c.hora,
                    c.estado,
                    c.motivo_consulta,
                    c.motivo_cancelacion,
                    c.fecha_cancelacion,
                    c.notificado,
                    c.fecha_notificacion,
                    p.dni AS paciente_dni,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    m.id_medico,
                    e.nombre AS especialidad,
                    CONCAT('MED-', LPAD(m.id_medico, 3, '0')) AS codigo_medico
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                {where_sql}
                ORDER BY c.fecha DESC, c.hora DESC, c.id_cita DESC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()
