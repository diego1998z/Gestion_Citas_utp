from typing import Any

from config.database import get_cursor, transaction


class HistorialCitaModel:
    """Acceso a datos de historiales clínicos generados desde citas."""

    def listar(self, busqueda: str | None = None) -> list[dict[str, Any]]:
        filtros: list[str] = []
        parametros: list[Any] = []

        if busqueda:
            termino = f"%{busqueda.strip()}%"
            filtros.append(
                """
                (
                    p.dni LIKE %s
                    OR p.nombres LIKE %s
                    OR p.apellidos LIKE %s
                    OR um.nombres LIKE %s
                    OR um.apellidos LIKE %s
                    OR e.nombre LIKE %s
                    OR hc.diagnostico LIKE %s
                    OR hc.observaciones LIKE %s
                )
                """
            )
            parametros.extend([termino, termino, termino, termino, termino, termino, termino, termino])

        where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    hc.id_historial_cita,
                    CONCAT('HIS-', LPAD(hc.id_historial_cita, 4, '0')) AS codigo,
                    hc.id_cita,
                    hc.diagnostico,
                    hc.tratamiento,
                    hc.observaciones,
                    hc.fecha_atencion,
                    c.fecha AS fecha_cita,
                    c.hora AS hora_cita,
                    c.estado AS estado_cita,
                    p.dni AS paciente_dni,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad
                FROM historial_cita hc
                INNER JOIN cita c ON c.id_cita = hc.id_cita
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                {where_sql}
                ORDER BY hc.fecha_atencion DESC, hc.id_historial_cita DESC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()

    def obtener_por_id(self, id_historial_cita: int) -> dict[str, Any] | None:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    hc.id_historial_cita,
                    CONCAT('HIS-', LPAD(hc.id_historial_cita, 4, '0')) AS codigo,
                    hc.id_cita,
                    hc.diagnostico,
                    hc.tratamiento,
                    hc.observaciones,
                    hc.fecha_atencion,
                    c.fecha AS fecha_cita,
                    c.hora AS hora_cita,
                    c.estado AS estado_cita,
                    p.dni AS paciente_dni,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad
                FROM historial_cita hc
                INNER JOIN cita c ON c.id_cita = hc.id_cita
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                WHERE hc.id_historial_cita = %s
                LIMIT 1
                """,
                (id_historial_cita,),
            )
            return cursor.fetchone()

    def crear_desde_cita(self, id_cita: int, observacion: str) -> int:
        """Crea historial solo si la cita ya está ATENDIDA."""
        with transaction(dictionary=True) as cursor:
            cita = self._obtener_cita_bloqueada(cursor, id_cita)
            if not cita:
                raise ValueError("La cita no existe.")
            if cita["estado"] != "ATENDIDA":
                raise ValueError("El historial solo se puede crear desde una cita atendida.")

            return self._insertar_historial(cursor, id_cita, observacion)

    def atender_y_crear_desde_cita(self, id_cita: int, observacion: str) -> int:
        """Marca la cita como ATENDIDA y crea historial en una sola transacción MVP."""
        with transaction(dictionary=True) as cursor:
            cita = self._obtener_cita_bloqueada(cursor, id_cita)
            if not cita:
                raise ValueError("La cita no existe.")

            if cita["estado"] == "ATENDIDA":
                return self._insertar_historial(cursor, id_cita, observacion)

            if cita["estado"] not in ("PENDIENTE", "CONFIRMADA"):
                raise ValueError("Solo se puede atender una cita pendiente o confirmada.")

            cursor.execute(
                """
                UPDATE cita
                SET estado = 'ATENDIDA'
                WHERE id_cita = %s
                """,
                (id_cita,),
            )
            return self._insertar_historial(cursor, id_cita, observacion)

    def _obtener_cita_bloqueada(self, cursor: Any, id_cita: int) -> dict[str, Any] | None:
        cursor.execute(
            """
            SELECT id_cita, estado
            FROM cita
            WHERE id_cita = %s
            FOR UPDATE
            """,
            (id_cita,),
        )
        return cursor.fetchone()

    def _insertar_historial(self, cursor: Any, id_cita: int, observacion: str) -> int:
        cursor.execute(
            """
            INSERT INTO historial_cita (
                id_cita,
                diagnostico,
                observaciones,
                fecha_atencion
            )
            VALUES (%s, %s, %s, NOW())
            """,
            (id_cita, observacion, observacion),
        )
        return int(cursor.lastrowid)
