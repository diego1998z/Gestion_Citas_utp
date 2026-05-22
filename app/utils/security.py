from werkzeug.security import check_password_hash


ROLES_VALIDOS = frozenset({"ADMINISTRADOR", "RECEPCIONISTA", "MEDICO"})
ESTADO_USUARIO_ACTIVO = "ACTIVO"


def verificar_password(password_hash: str, password: str) -> bool:
    """Verifica contraseña usando Werkzeug, sin reinventar criptografía."""
    if not password_hash or not password:
        return False

    return check_password_hash(password_hash, password)


def es_usuario_activo(usuario: dict | None) -> bool:
    return bool(usuario and usuario.get("estado") == ESTADO_USUARIO_ACTIVO)


def normalizar_roles(roles: tuple[str, ...]) -> set[str]:
    return {rol.strip().upper() for rol in roles if rol and rol.strip()}


def es_next_url_segura(next_url: str | None) -> bool:
    """Permite redirecciones internas simples y evita open redirects."""
    if not next_url:
        return False

    return next_url.startswith("/") and not next_url.startswith("//")
