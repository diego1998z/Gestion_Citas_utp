from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError

from app.models.paciente_model import PacienteModel
from app.utils.auth import roles_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.validators import validar_paciente_form


pacientes_bp = Blueprint("pacientes", __name__)
logger = get_logger(__name__)
paciente_model = PacienteModel()


@pacientes_bp.get("/pacientes")
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def index():
    busqueda = (request.args.get("q") or "").strip()
    pacientes = []

    try:
        pacientes = paciente_model.listar(busqueda or None)
    except MySQLError:
        log_error_tecnico(logger, "Error listando pacientes")
        flash("No pudimos cargar pacientes. Verificá la conexión a la base de datos.", "error")

    indicadores = _crear_indicadores(pacientes)
    segmentos = _crear_segmentos(pacientes)

    return render_template(
        "pacientes/index.html",
        page_title="Gestión de Pacientes",
        page_kicker="Registro y seguimiento",
        pacientes=pacientes,
        indicadores=indicadores,
        segmentos=segmentos,
        busqueda=busqueda,
    )


@pacientes_bp.route("/pacientes/nuevo", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def nuevo():
    form_data: dict = {}
    errors: dict[str, str] = {}

    if request.method == "POST":
        form_data, errors = validar_paciente_form(request.form)

        if not errors:
            try:
                id_paciente = paciente_model.crear(form_data)
            except MySQLError as error:
                log_error_tecnico(logger, "Error creando paciente")
                _flash_error_mysql(error, "No pudimos registrar el paciente. Revisá los datos e intentá nuevamente.")
            else:
                flash("Paciente registrado correctamente.", "success")
                return redirect(url_for("pacientes.editar", id_paciente=id_paciente))

    return render_template(
        "pacientes/form.html",
        page_title="Registrar paciente",
        page_kicker="Gestión de Pacientes",
        form_data=form_data,
        errors=errors,
        action_url=url_for("pacientes.nuevo"),
        submit_label="Registrar paciente",
    )


@pacientes_bp.route("/pacientes/<int:id_paciente>/editar", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def editar(id_paciente: int):
    errors: dict[str, str] = {}

    try:
        paciente = paciente_model.obtener_por_id(id_paciente)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo paciente")
        flash("No pudimos cargar el paciente solicitado.", "error")
        return redirect(url_for("pacientes.index"))

    if not paciente:
        abort(404)

    form_data = paciente

    if request.method == "POST":
        form_data, errors = validar_paciente_form(request.form)

        if not errors:
            try:
                paciente_model.actualizar(id_paciente, form_data)
            except MySQLError as error:
                log_error_tecnico(logger, "Error actualizando paciente")
                _flash_error_mysql(error, "No pudimos actualizar el paciente. Revisá los datos e intentá nuevamente.")
            else:
                flash("Paciente actualizado correctamente.", "success")
                return redirect(url_for("pacientes.index"))

    return render_template(
        "pacientes/form.html",
        page_title="Editar paciente",
        page_kicker="Gestión de Pacientes",
        form_data=form_data,
        errors=errors,
        action_url=url_for("pacientes.editar", id_paciente=id_paciente),
        submit_label="Guardar cambios",
    )


def _crear_indicadores(pacientes: list[dict]) -> list[dict]:
    total = len(pacientes)
    con_contacto = sum(1 for paciente in pacientes if paciente.get("telefono") or paciente.get("email"))
    con_cita = sum(1 for paciente in pacientes if paciente.get("ultima_cita"))

    return [
        {"titulo": "Pacientes listados", "valor": total, "detalle": "Según filtro actual", "tono": "primary"},
        {"titulo": "Con contacto", "valor": con_contacto, "detalle": "Teléfono o correo registrado", "tono": "success"},
        {"titulo": "Con cita registrada", "valor": con_cita, "detalle": "Historial vinculado a citas", "tono": "info"},
    ]


def _crear_segmentos(pacientes: list[dict]) -> list[dict]:
    menores = 0
    adultos = 0
    mayores = 0
    sin_fecha = 0

    for paciente in pacientes:
        edad = paciente.get("edad")
        if edad is None:
            sin_fecha += 1
        elif edad < 18:
            menores += 1
        elif edad >= 60:
            mayores += 1
        else:
            adultos += 1

    return [
        {"nombre": "Menores", "cantidad": menores},
        {"nombre": "Adultos", "cantidad": adultos},
        {"nombre": "Adultos mayores", "cantidad": mayores},
        {"nombre": "Sin fecha de nacimiento", "cantidad": sin_fecha},
    ]


def _flash_error_mysql(error: MySQLError, mensaje_default: str) -> None:
    if getattr(error, "errno", None) == 1062:
        flash("Ya existe un paciente con ese DNI o correo.", "error")
        return

    flash(mensaje_default, "error")
