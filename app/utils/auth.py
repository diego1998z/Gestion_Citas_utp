from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import abort, redirect, request, session, url_for

from app.utils.security import ROLES_VALIDOS, normalizar_roles


P = ParamSpec("P")
R = TypeVar("R")


def get_current_user() -> dict | None:
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return None

    return {
        "id_usuario": id_usuario,
        "username": session.get("username"),
        "nombre_usuario": session.get("username"),
        "rol": session.get("rol"),
        "nombres": session.get("nombres"),
        "apellidos": session.get("apellidos"),
        "nombre_completo": session.get("nombre_completo"),
    }


def login_required(view: Callable[P, R]) -> Callable[P, R]:
    @wraps(view)
    def wrapped_view(*args: P.args, **kwargs: P.kwargs) -> R:
        if not get_current_user():
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))

        return view(*args, **kwargs)

    return wrapped_view


def roles_required(*roles: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    roles_permitidos = normalizar_roles(roles)
    roles_invalidos = roles_permitidos - ROLES_VALIDOS

    if roles_invalidos:
        raise ValueError(f"Roles no válidos: {', '.join(sorted(roles_invalidos))}")

    def decorator(view: Callable[P, R]) -> Callable[P, R]:
        @wraps(view)
        @login_required
        def wrapped_view(*args: P.args, **kwargs: P.kwargs) -> R:
            usuario = get_current_user()
            if not usuario or usuario.get("rol") not in roles_permitidos:
                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
