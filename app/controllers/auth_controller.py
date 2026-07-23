from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error as MySQLError

from app.models.usuario_sistema_model import UsuarioSistemaModel
from app.utils.auth import get_current_user, login_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.security import es_next_url_segura, es_usuario_activo, verificar_password
from app.utils.validators import validar_login_form


auth_bp = Blueprint("auth", __name__)
logger = get_logger(__name__)
usuario_model = UsuarioSistemaModel()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("home.index"))

    form_data = {"username": ""}
    errors: dict[str, str] = {}

    if request.method == "POST":
        form_data, errors = validar_login_form(request.form)

        if not errors:
            try:
                usuario = usuario_model.buscar_por_username(form_data["username"])
            except MySQLError:
                log_error_tecnico(logger, "Error consultando usuario para login")
                flash("No pudimos procesar el inicio de sesión. Intentá nuevamente.", "error")
                return render_template("auth/login.html", form_data=form_data, errors=errors), 500

            credenciales_validas = bool(usuario) and verificar_password(
                usuario["password_hash"],
                form_data["password"],
            )

            if not credenciales_validas or not es_usuario_activo(usuario):
                flash("Usuario o contraseña incorrectos.", "error")
            else:
                rol_usuario = (usuario.get("rol") or "").strip().upper()
                rol_seleccionado = form_data["rol"]

                if rol_usuario != rol_seleccionado:
                    flash("Credenciales inválidas para el rol seleccionado.", "error")
                    return render_template("auth/login.html", form_data=form_data, errors=errors), 401

                session.clear()
                session["id_usuario"] = usuario["id_usuario"]
                session["username"] = usuario["username"]
                session["rol"] = rol_usuario
                session["nombres"] = usuario["nombres"]
                session["apellidos"] = usuario["apellidos"]
                session["nombre_completo"] = f"{usuario['nombres']} {usuario['apellidos']}"

                flash("Sesión iniciada correctamente.", "success")
                next_url = request.args.get("next")
                if es_next_url_segura(next_url):
                    return redirect(next_url)

                return redirect(url_for("home.index"))

    return render_template("auth/login.html", form_data=form_data, errors=errors)


@auth_bp.get("/auth/login")
def login_legacy():
    return redirect(url_for("auth.login"))


@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))
