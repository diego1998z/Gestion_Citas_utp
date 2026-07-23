from typing import Any

from config.database import get_cursor, transaction


class PacienteModel:
    """Acceso a datos de pacientes.

    Toda consulta SQL de pacientes vive acá. Los controladores validan y
    coordinan; las vistas solo renderizan datos ya preparados.
    """

    def listar(self, busqueda: str | None = None) -> list[dict[str, Any]]:
        return self._listar_con_filtros(busqueda=busqueda)

    def listar_por_medico(self, id_medico: int, busqueda: str | None = None) -> list[dict[str, Any]]:
        return self._listar_con_filtros(busqueda=busqueda, id_medico=id_medico)

    def _listar_con_filtros(self, busqueda: str | None = None, id_medico: int | None = None) -> list[dict[str, Any]]:
        filtros: list[str] = []
        parametros: list[Any] = []

        join_cita = ""
        if id_medico is not None:
            join_cita = "INNER JOIN cita c_medico ON c_medico.id_paciente = p.id_paciente"
            filtros.append("c_medico.id_medico = %s")
            parametros.append(id_medico)

        if busqueda:
            termino = f"%{busqueda.strip()}%"
            filtros.append(
                """
                (
                    p.dni LIKE %s
                    OR p.nombres LIKE %s
                    OR p.apellidos LIKE %s
                    OR p.telefono LIKE %s
                    OR p.email LIKE %s
                )
                """
            )
            parametros.extend([termino, termino, termino, termino, termino])

        where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                f"""
                SELECT
                    p.id_paciente,
                    CONCAT('PAC-', LPAD(p.id_paciente, 3, '0')) AS codigo,
                    p.dni,
                    p.nombres,
                    p.apellidos,
                    p.telefono,
                    p.email,
                    p.direccion,
                    p.fecha_nacimiento,
                    CASE
                        WHEN p.fecha_nacimiento IS NULL THEN NULL
                        ELSE TIMESTAMPDIFF(YEAR, p.fecha_nacimiento, CURDATE())
                    END AS edad,
                    (
                        SELECT MAX(c.fecha)
                        FROM cita c
                        WHERE c.id_paciente = p.id_paciente
                          AND (%s IS NULL OR c.id_medico = %s)
                    ) AS ultima_cita
                FROM paciente p
                {join_cita}
                {where_sql}
                GROUP BY
                    p.id_paciente,
                    p.dni,
                    p.nombres,
                    p.apellidos,
                    p.telefono,
                    p.email,
                    p.direccion,
                    p.fecha_nacimiento
                ORDER BY p.apellidos ASC, p.nombres ASC
                """,
                (id_medico, id_medico, *parametros),
            )
            return cursor.fetchall()

    def obtener_por_id(self, id_paciente: int) -> dict[str, Any] | None:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    id_paciente,
                    CONCAT('PAC-', LPAD(id_paciente, 3, '0')) AS codigo,
                    dni,
                    nombres,
                    apellidos,
                    telefono,
                    email,
                    fecha_nacimiento,
                    CASE
                        WHEN fecha_nacimiento IS NULL THEN NULL
                        ELSE TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE())
                    END AS edad,
                    direccion
                FROM paciente
                WHERE id_paciente = %s
                LIMIT 1
                """,
                (id_paciente,),
            )
            return cursor.fetchone()

    def tiene_cita_con_medico(self, id_paciente: int, id_medico: int) -> bool:
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT 1
                FROM cita
                WHERE id_paciente = %s
                  AND id_medico = %s
                LIMIT 1
                """,
                (id_paciente, id_medico),
            )
            return cursor.fetchone() is not None

    def crear(self, datos: dict[str, Any]) -> int:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                INSERT INTO paciente (
                    dni,
                    nombres,
                    apellidos,
                    telefono,
                    email,
                    fecha_nacimiento,
                    direccion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    datos["dni"],
                    datos["nombres"],
                    datos["apellidos"],
                    datos.get("telefono"),
                    datos.get("email"),
                    datos.get("fecha_nacimiento"),
                    datos.get("direccion"),
                ),
            )
            return int(cursor.lastrowid)

    def actualizar(self, id_paciente: int, datos: dict[str, Any]) -> None:
        with transaction(dictionary=True) as cursor:
            cursor.execute(
                """
                UPDATE paciente
                SET
                    dni = %s,
                    nombres = %s,
                    apellidos = %s,
                    telefono = %s,
                    email = %s,
                    fecha_nacimiento = %s,
                    direccion = %s
                WHERE id_paciente = %s
                """,
                (
                    datos["dni"],
                    datos["nombres"],
                    datos["apellidos"],
                    datos.get("telefono"),
                    datos.get("email"),
                    datos.get("fecha_nacimiento"),
                    datos.get("direccion"),
                    id_paciente,
                ),
            )
