from typing import Any

from config.database import get_cursor


class UsuarioSistemaModel:

    def buscar_por_username(self, username: str) -> dict[str, Any] | None:
        """Busca un usuario activo o inactivo por su nombre de usuario."""
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    id_usuario,
                    username,
                    username AS nombre_usuario,
                    password_hash,
                    rol,
                    estado,
                    nombres,
                    apellidos,
                    email
                FROM usuario_sistema
                WHERE username = %s
                LIMIT 1
                """,
                (username,),
            )
            return cursor.fetchone()

    def buscar_por_nombre_usuario(self, nombre_usuario: str) -> dict[str, Any] | None:
        """Alias semántico para la guía del proyecto."""
        return self.buscar_por_username(nombre_usuario)

    def obtener_por_id(self, id_usuario: int) -> dict[str, Any] | None:
        """Obtiene datos públicos del usuario autenticado."""
        with get_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    id_usuario,
                    username,
                    username AS nombre_usuario,
                    rol,
                    estado,
                    nombres,
                    apellidos,
                    email
                FROM usuario_sistema
                WHERE id_usuario = %s
                LIMIT 1
                """,
                (id_usuario,),
            )
            return cursor.fetchone()
