from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError
from werkzeug.security import generate_password_hash

from app.models.especialidad_model import EspecialidadModel
from app.models.horario_model import HorarioModel
from app.models.medico_model import MedicoModel
from app.utils.auth import roles_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.validators import (
    validar_especialidad_form,
    validar_horario_form,
    validar_medico_form,
)


medicos_bp = Blueprint("medicos", __name__)
logger = get_logger(__name__)
medico_model = MedicoModel()
especialidad_model = EspecialidadModel()
horario_model = HorarioModel()


@medicos_bp.get("/medicos")
@roles_required("ADMINISTRADOR")
def index():
    busqueda = (request.args.get("q") or "").strip()
    medicos = []
    especialidades = []

    try:
        medicos = medico_model.listar(busqueda or None)
        especialidades = especialidad_model.listar_con_total_medicos()
    except MySQLError:
        log_error_tecnico(logger, "Error listando médicos")
        flash("No pudimos cargar médicos y especialidades. Verificá la conexión a la base de datos.", "error")

    return render_template(
        "medicos/index.html",
        page_title="Gestión de Médicos",
        page_kicker="Administración de personal médico",
        medicos=medicos,
        especialidades=especialidades,
        busqueda=busqueda,
    )


@medicos_bp.route("/medicos/nuevo", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR")
def nuevo():
    form_data: dict = {"estado": "ACTIVO"}
    errors: dict[str, str] = {}
    especialidades = _listar_especialidades_seguro()

    if request.method == "POST":
        form_data, errors = validar_medico_form(request.form, requiere_password=True)

        if not errors:
            datos = dict(form_data)
            datos["password_hash"] = generate_password_hash(str(datos.pop("password")))

            try:
                id_medico = medico_model.crear(datos)
            except MySQLError as error:
                log_error_tecnico(logger, "Error creando médico")
                _flash_error_mysql(error, "No pudimos registrar el médico. Revisá los datos e intentá nuevamente.")
            else:
                flash("Médico registrado correctamente.", "success")
                return redirect(url_for("medicos.editar", id_medico=id_medico))

    return render_template(
        "medicos/form.html",
        page_title="Registrar médico",
        page_kicker="Gestión de Médicos",
        form_data=form_data,
        errors=errors,
        especialidades=especialidades,
        action_url=url_for("medicos.nuevo"),
        submit_label="Registrar médico",
        requiere_password=True,
        horarios=[],
    )


@medicos_bp.route("/medicos/<int:id_medico>/editar", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR")
def editar(id_medico: int):
    errors: dict[str, str] = {}
    especialidades = _listar_especialidades_seguro()

    try:
        medico = medico_model.obtener_por_id(id_medico)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo médico")
        flash("No pudimos cargar el médico solicitado.", "error")
        return redirect(url_for("medicos.index"))

    if not medico:
        abort(404)

    form_data = medico

    if request.method == "POST":
        form_data, errors = validar_medico_form(request.form, requiere_password=False)
        form_data["id_medico"] = id_medico

        if not errors:
            try:
                medico_model.actualizar(id_medico, form_data)
            except MySQLError as error:
                log_error_tecnico(logger, "Error actualizando médico")
                _flash_error_mysql(error, "No pudimos actualizar el médico. Revisá los datos e intentá nuevamente.")
            else:
                flash("Médico actualizado correctamente.", "success")
                return redirect(url_for("medicos.index"))

    horarios = _listar_horarios_seguro(id_medico)

    return render_template(
        "medicos/form.html",
        page_title="Editar médico",
        page_kicker="Gestión de Médicos",
        form_data=form_data,
        errors=errors,
        especialidades=especialidades,
        action_url=url_for("medicos.editar", id_medico=id_medico),
        submit_label="Guardar cambios",
        requiere_password=False,
        horarios=horarios,
    )


@medicos_bp.post("/especialidades/nuevo")
@roles_required("ADMINISTRADOR")
def crear_especialidad():
    form_data, errors = validar_especialidad_form(request.form)

    if errors:
        for mensaje in errors.values():
            flash(mensaje, "error")
        return redirect(url_for("medicos.index"))

    try:
        especialidad_model.crear(form_data)
    except MySQLError as error:
        log_error_tecnico(logger, "Error creando especialidad")
        if getattr(error, "errno", None) == 1062:
            flash("Ya existe una especialidad con ese nombre.", "error")
        else:
            flash("No pudimos registrar la especialidad. Intentá nuevamente.", "error")
    else:
        flash("Especialidad registrada correctamente.", "success")

    return redirect(url_for("medicos.index"))


@medicos_bp.post("/medicos/<int:id_medico>/horarios/nuevo")
@roles_required("ADMINISTRADOR")
def crear_horario(id_medico: int):
    form_data, errors = validar_horario_form(request.form, id_medico=id_medico)

    if errors:
        for mensaje in errors.values():
            flash(mensaje, "error")
        return redirect(url_for("medicos.editar", id_medico=id_medico))

    try:
        horario_model.crear(form_data)
    except MySQLError as error:
        log_error_tecnico(logger, "Error creando horario")
        if getattr(error, "errno", None) == 1062:
            flash("Ya existe un horario igual para ese médico.", "error")
        else:
            flash("No pudimos registrar el horario. Intentá nuevamente.", "error")
    else:
        flash("Horario registrado correctamente.", "success")

    return redirect(url_for("medicos.editar", id_medico=id_medico))


@medicos_bp.post("/horarios/<int:id_horario>/estado")
@roles_required("ADMINISTRADOR")
def actualizar_estado_horario(id_horario: int):
    id_medico = request.form.get("id_medico", type=int)
    estado = (request.form.get("estado") or "").strip().upper()

    if estado not in {"DISPONIBLE", "NO_DISPONIBLE"}:
        flash("Seleccioná un estado de horario válido.", "error")
        return redirect(url_for("medicos.index"))

    try:
        horario_model.actualizar_estado(id_horario, estado)
    except MySQLError:
        log_error_tecnico(logger, "Error actualizando estado de horario")
        flash("No pudimos actualizar el estado del horario.", "error")
    else:
        flash("Estado de horario actualizado correctamente.", "success")

    if id_medico:
        return redirect(url_for("medicos.editar", id_medico=id_medico))

    return redirect(url_for("medicos.index"))


@medicos_bp.get("/medicos/<int:id_medico>/disponibilidad")
@roles_required("ADMINISTRADOR")
def disponibilidad(id_medico: int):
    try:
        horarios = horario_model.listar_por_medico(id_medico)
    except MySQLError:
        log_error_tecnico(logger, "Error consultando disponibilidad médica")
        return jsonify({"horarios": [], "mensaje": "No pudimos cargar la disponibilidad."}), 500

    return jsonify(
        {
            "horarios": [
                {
                    "id_horario": horario["id_horario"],
                    "fecha": str(horario["fecha"]),
                    "hora_inicio": str(horario["hora_inicio"]),
                    "hora_fin": str(horario["hora_fin"]),
                    "estado": horario["estado"],
                }
                for horario in horarios
            ]
        }
    )


def _listar_especialidades_seguro() -> list[dict]:
    try:
        return especialidad_model.listar()
    except MySQLError:
        log_error_tecnico(logger, "Error listando especialidades")
        flash("No pudimos cargar las especialidades.", "error")
        return []


def _listar_horarios_seguro(id_medico: int) -> list[dict]:
    try:
        return horario_model.listar_por_medico(id_medico)
    except MySQLError:
        log_error_tecnico(logger, "Error listando horarios del médico")
        flash("No pudimos cargar los horarios del médico.", "error")
        return []


def _flash_error_mysql(error: MySQLError, mensaje_default: str) -> None:
    if getattr(error, "errno", None) == 1062:
        flash("Ya existe un usuario, correo o colegiatura con esos datos.", "error")
        return

    flash(mensaje_default, "error")
