from typing import Any

from config.database import get_cursor, transaction


class MedicoModel:
    """Acceso a datos de médicos y su usuario asociado."""

    def listar(self, busqueda: str | None = None) -> list[dict[str, Any]]:
        filtros: list[str] = []
        parametros: list[Any] = []

        if busqueda:
            termino = f"%{busqueda.strip()}%"
            filtros.append(
                """
                (
                    u.nombres LIKE %s
                    OR u.apellidos LIKE %s
                    OR u.email LIKE %s
                    OR u.telefono LIKE %s
                    OR e.nombre LIKE %s
                    OR m.numero_colegiatura LIKE %s
                )
                """
            )
            parametros.extend([termino, termino, termino, termino, termino, termino])

        where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    m.id_medico,
                    CONCAT('MED-', LPAD(m.id_medico, 3, '0')) AS codigo,
                    m.id_usuario,
                    m.id_especialidad,
                    m.numero_colegiatura,
                    u.username,
                    u.nombres,
                    u.apellidos,
                    u.email,
                    u.telefono,
                    u.estado,
                    e.nombre AS especialidad,
                    COALESCE(
                        (
                            SELECT CONCAT(
                                DATE_FORMAT(MIN(h.fecha), '%d/%m/%Y'),
                                ' · ',
                                TIME_FORMAT(MIN(h.hora_inicio), '%H:%i'),
                                ' - ',
                                TIME_FORMAT(MAX(h.hora_fin), '%H:%i')
                            )
                            FROM horario h
                            WHERE h.id_medico = m.id_medico
                              AND h.estado = 'DISPONIBLE'
                        ),
                        'Sin horario activo'
                    ) AS horario
                FROM medico m
                INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = m.id_especialidad
                {where_sql}
                ORDER BY u.apellidos ASC, u.nombres ASC
                """,
                tuple(parametros),
            )
            return cursor.fetchall()

    def obtener_por_id(self, id_medico: int) -> dict[str, Any] | None:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    m.id_medico,
                    m.id_usuario,
                    m.id_especialidad,
                    m.numero_colegiatura,
                    u.username,
                    u.nombres,
                    u.apellidos,
                    u.email,
                    u.telefono,
                    u.estado
                FROM medico m
                INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
                WHERE m.id_medico = %s
                LIMIT 1
                """,
                (id_medico,),
            )
            return cursor.fetchone()

    def crear(self, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO usuario_sistema (
                    username,
                    password_hash,
                    rol,
                    estado,
                    nombres,
                    apellidos,
                    email,
                    telefono
                )
                VALUES (%s, %s, 'MEDICO', %s, %s, %s, %s, %s)
                """,
                (
                    datos["username"],
                    datos["password_hash"],
                    datos["estado"],
                    datos["nombres"],
                    datos["apellidos"],
                    datos.get("email"),
                    datos.get("telefono"),
                ),
            )
            id_usuario = int(cursor.lastrowid)

            cursor.execute(
                """
                INSERT INTO medico (
                    id_usuario,
                    id_especialidad,
                    numero_colegiatura
                )
                VALUES (%s, %s, %s)
                """,
                (
                    id_usuario,
                    datos["id_especialidad"],
                    datos["numero_colegiatura"],
                ),
            )
            return int(cursor.lastrowid)

    def actualizar(self, id_medico: int, datos: dict[str, Any]) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id_usuario
                FROM medico
                WHERE id_medico = %s
                LIMIT 1
                """,
                (id_medico,),
            )
            medico = cursor.fetchone()
            if not medico:
                return

            cursor.execute(
                """
                UPDATE usuario_sistema
                SET
                    username = %s,
                    estado = %s,
                    nombres = %s,
                    apellidos = %s,
                    email = %s,
                    telefono = %s
                WHERE id_usuario = %s
                """,
                (
                    datos["username"],
                    datos["estado"],
                    datos["nombres"],
                    datos["apellidos"],
                    datos.get("email"),
                    datos.get("telefono"),
                    medico["id_usuario"],
                ),
            )

            cursor.execute(
                """
                UPDATE medico
                SET
                    id_especialidad = %s,
                    numero_colegiatura = %s
                WHERE id_medico = %s
                """,
                (
                    datos["id_especialidad"],
                    datos["numero_colegiatura"],
                    id_medico,
                ),
            )
