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
        return self._listar_con_filtros(busqueda=busqueda)

    def listar_por_medico(self, id_medico: int, filtros: dict[str, Any] | str | None = None) -> list[dict[str, Any]]:
        busqueda = self._extraer_busqueda(filtros)
        return self._listar_con_filtros(busqueda=busqueda, id_medico=id_medico)

    def obtener_dashboard_operativo(self) -> dict[str, Any]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    COUNT(CASE WHEN c.fecha = CURDATE() THEN 1 END) AS citas_hoy,
                    COUNT(CASE WHEN c.fecha = CURDATE() AND c.estado = 'PENDIENTE' THEN 1 END) AS pendientes_hoy,
                    COUNT(CASE WHEN c.estado = 'CANCELADA' AND c.fecha >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN 1 END) AS canceladas_24h,
                    COUNT(CASE WHEN c.estado IN ('PENDIENTE', 'CONFIRMADA') THEN 1 END) AS citas_activas,
                    COUNT(CASE WHEN c.estado IN ('PENDIENTE', 'CONFIRMADA') AND c.notificado = FALSE THEN 1 END) AS pendientes_notificacion
                FROM cita c
                """
            )
            resumen_citas = cursor.fetchone() or {}

            cursor.execute("SELECT COUNT(*) AS total FROM paciente")
            total_pacientes = (cursor.fetchone() or {}).get("total", 0)

            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT m.id_medico) AS medicos_disponibles,
                    COUNT(DISTINCT m.id_especialidad) AS especialidades_disponibles
                FROM medico m
                INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
                INNER JOIN horario h ON h.id_medico = m.id_medico
                WHERE u.estado = 'ACTIVO'
                  AND h.estado = 'DISPONIBLE'
                  AND h.fecha >= CURDATE()
                """
            )
            disponibilidad = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT
                    c.id_cita,
                    c.fecha,
                    c.hora,
                    c.estado,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                WHERE c.estado IN ('PENDIENTE', 'CONFIRMADA')
                  AND c.fecha >= CURDATE()
                ORDER BY c.fecha ASC, c.hora ASC, c.id_cita ASC
                LIMIT 5
                """
            )
            proximas_citas = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    ce.tipo_evento,
                    ce.created_at,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(ua.nombres, ' ', ua.apellidos) AS actor
                FROM cita_evento ce
                INNER JOIN cita c ON c.id_cita = ce.id_cita
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                LEFT JOIN usuario_sistema ua ON ua.id_usuario = ce.id_usuario_actor
                ORDER BY ce.created_at DESC, ce.id_cita_evento DESC
                LIMIT 3
                """
            )
            actividad = cursor.fetchall()

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM medico m
                INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
                LEFT JOIN horario h ON h.id_medico = m.id_medico
                    AND h.estado = 'DISPONIBLE'
                    AND h.fecha >= CURDATE()
                WHERE u.estado = 'ACTIVO'
                  AND h.id_horario IS NULL
                """
            )
            medicos_sin_horario = (cursor.fetchone() or {}).get("total", 0)

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM paciente
                WHERE email IS NULL OR email = '' OR telefono IS NULL OR telefono = ''
                """
            )
            pacientes_contacto_incompleto = (cursor.fetchone() or {}).get("total", 0)

            return {
                "resumen_citas": resumen_citas,
                "total_pacientes": total_pacientes,
                "disponibilidad": disponibilidad,
                "proximas_citas": proximas_citas,
                "actividad": actividad,
                "medicos_sin_horario": medicos_sin_horario,
                "pacientes_contacto_incompleto": pacientes_contacto_incompleto,
            }

    def obtener_por_id(self, id_cita: int) -> dict[str, Any] | None:
        return self._obtener_por_id_con_filtros(id_cita=id_cita)

    def obtener_por_id_y_medico(self, id_cita: int, id_medico: int) -> dict[str, Any] | None:
        return self._obtener_por_id_con_filtros(id_cita=id_cita, id_medico=id_medico)

    def es_notificable(self, cita: dict[str, Any]) -> bool:
        return cita.get("estado") in ESTADOS_CITA_ACTIVA

    def _listar_con_filtros(self, busqueda: str | None = None, id_medico: int | None = None) -> list[dict[str, Any]]:
        filtros: list[str] = []
        parametros: list[Any] = []

        if id_medico is not None:
            filtros.append("c.id_medico = %s")
            parametros.append(id_medico)

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
                    p.email AS paciente_email,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad,
                    CONCAT('MED-', LPAD(m.id_medico, 3, '0')) AS codigo_medico,
                    CASE
                        WHEN hc.id_historial_cita IS NULL THEN 0
                        ELSE 1
                    END AS tiene_historial,
                    ue.tipo_evento AS ultimo_evento,
                    ue.created_at AS fecha_ultimo_evento
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                LEFT JOIN historial_cita hc ON hc.id_cita = c.id_cita
                LEFT JOIN cita_evento ue ON ue.id_cita_evento = (
                    SELECT ce.id_cita_evento
                    FROM cita_evento ce
                    WHERE ce.id_cita = c.id_cita
                    ORDER BY ce.created_at DESC, ce.id_cita_evento DESC
                    LIMIT 1
                )
                {where_sql}
                ORDER BY c.fecha DESC, c.hora DESC, c.id_cita DESC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()

    def _obtener_por_id_con_filtros(self, id_cita: int, id_medico: int | None = None) -> dict[str, Any] | None:
        filtros = ["c.id_cita = %s"]
        parametros: list[Any] = [id_cita]

        if id_medico is not None:
            filtros.append("c.id_medico = %s")
            parametros.append(id_medico)

        where_sql = " AND ".join(filtros)

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
                    p.email AS paciente_email,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico,
                    e.nombre AS especialidad,
                    CASE
                        WHEN hc.id_historial_cita IS NULL THEN 0
                        ELSE 1
                    END AS tiene_historial,
                    ue.tipo_evento AS ultimo_evento,
                    ue.created_at AS fecha_ultimo_evento
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                LEFT JOIN historial_cita hc ON hc.id_cita = c.id_cita
                LEFT JOIN cita_evento ue ON ue.id_cita_evento = (
                    SELECT ce.id_cita_evento
                    FROM cita_evento ce
                    WHERE ce.id_cita = c.id_cita
                    ORDER BY ce.created_at DESC, ce.id_cita_evento DESC
                    LIMIT 1
                )
                WHERE {where_sql}
                LIMIT 1
                """,
                tuple(parametros),
            )
            return cursor.fetchone()

    def _extraer_busqueda(self, filtros: dict[str, Any] | str | None) -> str | None:
        if filtros is None:
            return None

        if isinstance(filtros, str):
            busqueda = filtros.strip()
            return busqueda or None

        busqueda = str(filtros.get("busqueda") or filtros.get("q") or "").strip()
        return busqueda or None

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

    def cancelar_cita(self, id_cita: int, motivo: str, id_usuario_actor: int | None = None) -> None:
        with transaction(dictionary=True) as cursor:
            cita = self._obtener_cita_bloqueada(cursor, id_cita)
            if not cita:
                raise ValueError("La cita no existe.")

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
            self._registrar_evento(cursor, id_cita, "CANCELADA", id_usuario_actor=id_usuario_actor, motivo=motivo)

    def notificar_paciente(self, id_cita: int) -> None:
        self.marcar_notificada(id_cita)

    def marcar_notificada(self, id_cita: int, id_usuario_actor: int | None = None) -> None:
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
            self._registrar_evento(cursor, id_cita, "NOTIFICADA", id_usuario_actor=id_usuario_actor)

    def registrar_notificacion_fallida(self, id_cita: int, detalle: str, id_usuario_actor: int | None = None) -> None:
        with transaction(dictionary=True) as cursor:
            self._registrar_evento(
                cursor,
                id_cita,
                "NOTIFICACION_FALLIDA",
                id_usuario_actor=id_usuario_actor,
                detalle=detalle[:255],
            )

    def reprogramar_cita(self, id_cita_original: int, datos: dict[str, Any], id_usuario_actor: int | None = None) -> int:
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
            nueva_cita = int(cursor.lastrowid)
            self._registrar_evento(
                cursor,
                id_cita_original,
                "REPROGRAMADA",
                id_usuario_actor=id_usuario_actor,
                id_cita_relacionada=nueva_cita,
                fecha_anterior=cita_original["fecha"],
                hora_anterior=cita_original["hora"],
                fecha_nueva=nueva_fecha,
                hora_nueva=nueva_hora,
                motivo=datos.get("motivo_consulta") or cita_original.get("motivo_consulta"),
            )
            return nueva_cita

    def crear_seguimiento(self, id_cita_original: int, datos: dict[str, Any], id_usuario_actor: int | None = None) -> int:
        with transaction(dictionary=True) as cursor:
            cita_original = self._obtener_cita_bloqueada(cursor, id_cita_original)
            if not cita_original:
                raise ValueError("La cita original no existe.")
            if cita_original["estado"] not in ("PENDIENTE", "CONFIRMADA", "ATENDIDA"):
                raise ValueError("Solo se puede crear seguimiento desde una cita activa o atendida.")

            fecha = str(datos["fecha"])
            hora = str(datos["hora"])
            id_medico = int(cita_original["id_medico"])

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
                    id_medico,
                    cita_original.get("id_recepcionista"),
                    id_cita_original,
                    fecha,
                    hora,
                    datos.get("motivo_consulta") or "Seguimiento médico",
                ),
            )
            nueva_cita = int(cursor.lastrowid)
            self._registrar_evento(
                cursor,
                id_cita_original,
                "SEGUIMIENTO_CREADO",
                id_usuario_actor=id_usuario_actor,
                id_cita_relacionada=nueva_cita,
                fecha_nueva=fecha,
                hora_nueva=hora,
                motivo=datos.get("motivo_consulta"),
            )
            return nueva_cita

    def listar_pendientes_recordatorio(self) -> list[dict[str, Any]]:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    c.id_cita,
                    c.fecha,
                    c.hora,
                    p.email AS paciente_email,
                    CONCAT(p.nombres, ' ', p.apellidos) AS paciente,
                    CONCAT(um.nombres, ' ', um.apellidos) AS medico
                FROM cita c
                INNER JOIN paciente p ON p.id_paciente = c.id_paciente
                INNER JOIN medico m ON m.id_medico = c.id_medico
                INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
                WHERE c.estado IN ('PENDIENTE', 'CONFIRMADA')
                  AND c.notificado = FALSE
                  AND p.email IS NOT NULL
                  AND TIMESTAMP(c.fecha, c.hora) BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
                ORDER BY c.fecha ASC, c.hora ASC
                """
            )
            return cursor.fetchall()

    def marcar_atendida(self, id_cita: int, id_usuario_actor: int | None = None) -> None:
        self._actualizar_estado_final(id_cita, "ATENDIDA", "Solo se pueden atender citas pendientes o confirmadas.", id_usuario_actor)

    def marcar_no_asistio(self, id_cita: int, id_usuario_actor: int | None = None) -> None:
        self._actualizar_estado_final(id_cita, "NO_ASISTIO", "Solo se pueden marcar como no asistidas citas pendientes o confirmadas.", id_usuario_actor)

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

    def _obtener_cita_bloqueada(self, cursor: Any, id_cita: int) -> dict[str, Any] | None:
        cursor.execute(
            """
            SELECT id_cita, id_paciente, id_medico, id_recepcionista, fecha, hora, estado, motivo_consulta
            FROM cita
            WHERE id_cita = %s
            FOR UPDATE
            """,
            (id_cita,),
        )
        return cursor.fetchone()

    def _registrar_evento(
        self,
        cursor: Any,
        id_cita: int,
        tipo_evento: str,
        id_usuario_actor: int | None = None,
        id_cita_relacionada: int | None = None,
        fecha_anterior: Any | None = None,
        hora_anterior: Any | None = None,
        fecha_nueva: Any | None = None,
        hora_nueva: Any | None = None,
        motivo: str | None = None,
        detalle: str | None = None,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO cita_evento (
                id_cita,
                id_usuario_actor,
                id_cita_relacionada,
                tipo_evento,
                fecha_anterior,
                hora_anterior,
                fecha_nueva,
                hora_nueva,
                motivo,
                detalle
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                id_cita,
                id_usuario_actor,
                id_cita_relacionada,
                tipo_evento,
                fecha_anterior,
                hora_anterior,
                fecha_nueva,
                hora_nueva,
                motivo,
                detalle,
            ),
        )

    def _actualizar_estado_final(self, id_cita: int, estado: str, mensaje_error: str, id_usuario_actor: int | None = None) -> None:
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
            self._registrar_evento(cursor, id_cita, estado, id_usuario_actor=id_usuario_actor)

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
