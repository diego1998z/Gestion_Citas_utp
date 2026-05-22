from typing import Any

from config.database import get_cursor, transaction


ESTADOS_CITA_ACTIVA = ("PENDIENTE", "CONFIRMADA")
ESTADOS_CITA_FINAL = ("CANCELADA", "ATENDIDA", "NO_ASISTIO", "REPROGRAMADA")


class CitaModel:
    """Acceso a datos de citas médicas.

    Este modelo concentra toda consulta SQL del flujo de citas: agenda,
    disponibilidad, programación, cancelación, notificación y reprogramación.
    """

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
                    OR c.estado LIKE %s
                )
                """
            )
            parametros.extend([termino, termino, termino, termino, termino, termino, termino])

        where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    c.id_cita,
                    CONCAT('CIT-', LPAD(c.id_cita, 4, '0')) AS codigo,
                    c.id_paciente,
                    c.id_medico,
                    c.id_recepcionista,
                    c.id_cita_origen,
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
                    e.nombre AS especialidad,
                    CONCAT('MED-', LPAD(m.id_medico, 3, '0')) AS codigo_medico,
                    CASE
                        WHEN hc.id_historial_cita IS NULL THEN 0
                        ELSE 1
                    END AS tiene_historial
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                LEFT JOIN historial_cita hc ON hc.id_cita = c.id_cita
                {where_sql}
                ORDER BY c.fecha DESC, c.hora DESC, c.id_cita DESC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()

    def obtener_por_id(self, id_cita: int) -> dict[str, Any] | None:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    c.id_cita,
                    CONCAT('CIT-', LPAD(c.id_cita, 4, '0')) AS codigo,
                    c.id_paciente,
                    c.id_medico,
                    c.id_recepcionista,
                    c.id_cita_origen,
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
                    e.nombre AS especialidad,
                    CASE
                        WHEN hc.id_historial_cita IS NULL THEN 0
                        ELSE 1
                    END AS tiene_historial
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                LEFT JOIN historial_cita hc ON hc.id_cita = c.id_cita
                WHERE c.id_cita = %s
                LIMIT 1
                """,
                (id_cita,),
            )
            return cursor.fetchone()

    def listar_horarios_disponibles(self, id_medico: int | None = None) -> list[dict[str, Any]]:
        filtros = ["h.estado = 'DISPONIBLE'"]
        parametros: list[Any] = []

        if id_medico:
            filtros.append("h.id_medico = %s")
            parametros.append(id_medico)

        where_sql = " AND ".join(filtros)

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    h.id_horario,
                    h.id_medico,
                    h.fecha,
                    h.hora_inicio,
                    h.hora_fin,
                    h.estado,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad
                FROM horario h
                INNER JOIN medico m ON m.id_medico = h.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                WHERE {where_sql}
                ORDER BY h.fecha ASC, h.hora_inicio ASC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()

    def validar_disponibilidad_medico(self, id_medico: int, fecha: str, hora: str) -> bool:
        with get_cursor(dictionary=True) as (_, cursor):
            return self._medico_tiene_horario(cursor, id_medico, fecha, hora) and self._esta_libre(
                cursor,
                id_medico,
                fecha,
                hora,
            )

    def programar_cita(self, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            id_medico = int(datos["id_medico"])
            fecha = str(datos["fecha"])
            hora = str(datos["hora"])

            if not self._medico_tiene_horario(cursor, id_medico, fecha, hora):
                raise ValueError("El médico no tiene horario disponible para esa fecha y hora.")

            if not self._esta_libre(cursor, id_medico, fecha, hora):
                raise ValueError("Ya existe una cita activa para ese médico en esa fecha y hora.")

            cursor.execute(
                """
                INSERT INTO cita (
                    id_paciente,
                    id_medico,
                    id_recepcionista,
                    fecha,
                    hora,
                    estado,
                    motivo_consulta
                )
                VALUES (%s, %s, %s, %s, %s, 'PENDIENTE', %s)
                """,
                (
                    datos["id_paciente"],
                    id_medico,
                    datos.get("id_recepcionista"),
                    fecha,
                    hora,
                    datos.get("motivo_consulta"),
                ),
            )
            return int(cursor.lastrowid)

    def cancelar_cita(self, id_cita: int, motivo: str) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                UPDATE cita
                SET
                    estado = 'CANCELADA',
                    motivo_cancelacion = %s,
                    fecha_cancelacion = NOW()
                WHERE id_cita = %s
                  AND estado IN ('PENDIENTE', 'CONFIRMADA')
                """,
                (motivo, id_cita),
            )
            if cursor.rowcount == 0:
                raise ValueError("Solo se pueden cancelar citas pendientes o confirmadas.")

    def notificar_paciente(self, id_cita: int) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                UPDATE cita
                SET
                    notificado = TRUE,
                    fecha_notificacion = NOW()
                WHERE id_cita = %s
                  AND estado IN ('PENDIENTE', 'CONFIRMADA')
                """,
                (id_cita,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Solo se pueden notificar citas pendientes o confirmadas.")

    def reprogramar_cita(self, id_cita_original: int, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    id_cita,
                    id_paciente,
                    id_medico,
                    id_recepcionista,
                    fecha,
                    hora,
                    estado,
                    motivo_consulta
                FROM cita
                WHERE id_cita = %s
                FOR UPDATE
                """,
                (id_cita_original,),
            )
            cita_original = cursor.fetchone()

            if not cita_original:
                raise ValueError("La cita original no existe.")

            if cita_original["estado"] not in ESTADOS_CITA_ACTIVA:
                raise ValueError("Solo se pueden reprogramar citas pendientes o confirmadas.")

            nuevo_id_medico = int(datos.get("id_medico") or cita_original["id_medico"])
            nueva_fecha = str(datos["fecha"])
            nueva_hora = str(datos["hora"])

            if (
                nuevo_id_medico == cita_original["id_medico"]
                and nueva_fecha == str(cita_original["fecha"])
                and nueva_hora == self._normalizar_hora(cita_original["hora"])
            ):
                raise ValueError("La nueva fecha u hora debe ser distinta de la cita original.")

            if not self._medico_tiene_horario(cursor, nuevo_id_medico, nueva_fecha, nueva_hora):
                raise ValueError("El médico no tiene horario disponible para la nueva fecha y hora.")

            if not self._esta_libre(cursor, nuevo_id_medico, nueva_fecha, nueva_hora, id_cita_excluir=id_cita_original):
                raise ValueError("Ya existe una cita activa para ese médico en la nueva fecha y hora.")

            cursor.execute(
                """
                UPDATE cita
                SET estado = 'REPROGRAMADA'
                WHERE id_cita = %s
                """,
                (id_cita_original,),
            )

            cursor.execute(
                """
                INSERT INTO cita (
                    id_paciente,
                    id_medico,
                    id_recepcionista,
                    id_cita_origen,
                    fecha,
                    hora,
                    estado,
                    motivo_consulta
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
                """,
                (
                    cita_original["id_paciente"],
                    nuevo_id_medico,
                    datos.get("id_recepcionista") or cita_original.get("id_recepcionista"),
                    id_cita_original,
                    nueva_fecha,
                    nueva_hora,
                    datos.get("motivo_consulta") or cita_original.get("motivo_consulta"),
                ),
            )
            return int(cursor.lastrowid)

    def marcar_atendida(self, id_cita: int) -> None:
        self._actualizar_estado_final(id_cita, "ATENDIDA", "Solo se pueden atender citas pendientes o confirmadas.")

    def marcar_no_asistio(self, id_cita: int) -> None:
        self._actualizar_estado_final(id_cita, "NO_ASISTIO", "Solo se pueden marcar como no asistidas citas pendientes o confirmadas.")

    def obtener_id_recepcionista_por_usuario(self, id_usuario: int) -> int | None:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT id_recepcionista
                FROM recepcionista
                WHERE id_usuario = %s
                LIMIT 1
                """,
                (id_usuario,),
            )
            recepcionista = cursor.fetchone()
            return int(recepcionista["id_recepcionista"]) if recepcionista else None

    def _actualizar_estado_final(self, id_cita: int, estado: str, mensaje_error: str) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                UPDATE cita
                SET estado = %s
                WHERE id_cita = %s
                  AND estado IN ('PENDIENTE', 'CONFIRMADA')
                """,
                (estado, id_cita),
            )
            if cursor.rowcount == 0:
                raise ValueError(mensaje_error)

    def _medico_tiene_horario(self, cursor: Any, id_medico: int, fecha: str, hora: str) -> bool:
        cursor.execute(
            """
            SELECT id_horario
            FROM horario
            WHERE id_medico = %s
              AND fecha = %s
              AND estado = 'DISPONIBLE'
              AND %s >= TIME_FORMAT(hora_inicio, '%%H:%%i')
              AND %s < TIME_FORMAT(hora_fin, '%%H:%%i')
            LIMIT 1
            """,
            (id_medico, fecha, hora, hora),
        )
        return cursor.fetchone() is not None

    def _esta_libre(
        self,
        cursor: Any,
        id_medico: int,
        fecha: str,
        hora: str,
        id_cita_excluir: int | None = None,
    ) -> bool:
        parametros: list[Any] = [id_medico, fecha, hora]
        filtro_exclusion = ""

        if id_cita_excluir:
            filtro_exclusion = "AND id_cita <> %s"
            parametros.append(id_cita_excluir)

        cursor.execute(
            f"""
            SELECT id_cita
            FROM cita
            WHERE id_medico = %s
              AND fecha = %s
              AND TIME_FORMAT(hora, '%%H:%%i') = %s
              AND estado IN ('PENDIENTE', 'CONFIRMADA')
              {filtro_exclusion}
            LIMIT 1
            FOR UPDATE
            """,
            tuple(parametros),
        )
        return cursor.fetchone() is None

    def _normalizar_hora(self, valor: Any) -> str:
        partes = str(valor).split(":")
        if len(partes) < 2:
            return str(valor)

        return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
