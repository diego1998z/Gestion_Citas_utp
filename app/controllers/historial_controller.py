from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError

from app.models.cita_model import CitaModel
from app.models.historial_cita_model import HistorialCitaModel
from app.models.medico_model import MedicoModel
from app.utils.auth import get_current_user, roles_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.validators import validar_historial_form


historial_bp = Blueprint("historial", __name__)
logger = get_logger(__name__)
historial_model = HistorialCitaModel()
cita_model = CitaModel()
medico_model = MedicoModel()


@historial_bp.get("/historial")
@roles_required("ADMINISTRADOR", "MEDICO", "RECEPCIONISTA")
def index():
    busqueda = (request.args.get("q") or "").strip()
    historiales = []
    usuario = get_current_user()

    try:
        if usuario and usuario.get("rol") == "MEDICO":
            id_medico = _obtener_id_medico_actual()
            historiales = historial_model.listar_por_medico(id_medico, busqueda or None) if id_medico else []
        else:
            historiales = historial_model.listar(busqueda or None)
    except MySQLError:
        log_error_tecnico(logger, "Error listando historial")
        flash("No pudimos cargar el historial de citas.", "error")

    return render_template(
        "historial/index.html",
        page_title="Historial de Citas",
        page_kicker="Registro de atenciones",
        historiales=historiales,
        indicadores=_crear_indicadores(historiales, usuario.get("rol") if usuario else None),
        busqueda=busqueda,
        rol_actual=usuario.get("rol") if usuario else None,
    )


@historial_bp.route("/historial/cita/<int:id_cita>/nuevo", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "MEDICO")
def nuevo_desde_cita(id_cita: int):
    usuario = get_current_user()

    try:
        if usuario and usuario.get("rol") == "MEDICO":
            id_medico = _obtener_id_medico_actual()
            if not id_medico:
                return redirect(url_for("citas.index"))
            cita = cita_model.obtener_por_id_y_medico(id_cita, id_medico)
        else:
            cita = cita_model.obtener_por_id(id_cita)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo cita para historial")
        flash("No pudimos cargar la cita solicitada.", "error")
        return redirect(url_for("citas.index"))

    if not cita:
        if usuario and usuario.get("rol") == "MEDICO":
            flash("No tenés acceso a esa cita médica.", "error")
            return redirect(url_for("citas.index"))
        abort(404)

    if cita.get("tiene_historial"):
        return redirect(url_for("historial.editar_desde_cita", id_cita=id_cita))

    if cita["estado"] not in {"PENDIENTE", "CONFIRMADA", "ATENDIDA"}:
        flash("Solo se puede crear historial para citas pendientes, confirmadas o atendidas.", "error")
        return redirect(url_for("citas.index"))

    form_data: dict = {"observacion": ""}
    errors: dict[str, str] = {}

    if request.method == "POST":
        form_data, errors = validar_historial_form(request.form)

        if not errors:
            try:
                if cita["estado"] == "ATENDIDA":
                    historial_model.crear_desde_cita(id_cita, str(form_data["observacion"]))
                else:
                    historial_model.atender_y_crear_desde_cita(id_cita, str(form_data["observacion"]), _obtener_id_usuario_actual())
            except ValueError as error:
                flash(str(error), "error")
            except MySQLError as error:
                log_error_tecnico(logger, "Error creando historial desde cita")
                _flash_error_mysql(error, "No pudimos registrar el historial. Intentá nuevamente.")
            else:
                flash("Historial registrado correctamente.", "success")
                return redirect(url_for("historial.index"))

    return render_template(
        "historial/form.html",
        page_title="Registrar atención",
        page_kicker="Historial de Citas",
        cita=cita,
        form_data=form_data,
        errors=errors,
        action_url=url_for("historial.nuevo_desde_cita", id_cita=id_cita),
        submit_label="Registrar historial",
    )


@historial_bp.route("/historial/cita/<int:id_cita>/editar", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "MEDICO")
def editar_desde_cita(id_cita: int):
    usuario = get_current_user()

    try:
        if usuario and usuario.get("rol") == "MEDICO":
            id_medico = _obtener_id_medico_actual()
            if not id_medico:
                return redirect(url_for("citas.index"))
            cita = cita_model.obtener_por_id_y_medico(id_cita, id_medico)
        else:
            cita = cita_model.obtener_por_id(id_cita)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo cita para editar historial")
        flash("No pudimos cargar la cita solicitada.", "error")
        return redirect(url_for("citas.index"))

    if not cita:
        if usuario and usuario.get("rol") == "MEDICO":
            flash("No tenés acceso a esa cita médica.", "error")
            return redirect(url_for("citas.index"))
        abort(404)

    if cita["estado"] != "ATENDIDA":
        flash("Solo se puede editar la observación de citas atendidas.", "error")
        return redirect(url_for("citas.index"))

    try:
        historial = historial_model.obtener_por_cita(id_cita)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo historial para editar")
        flash("No pudimos cargar el historial de la cita.", "error")
        return redirect(url_for("citas.index"))

    if not historial:
        return redirect(url_for("historial.nuevo_desde_cita", id_cita=id_cita))

    form_data: dict = {"observacion": historial.get("observaciones") or historial.get("diagnostico") or ""}
    errors: dict[str, str] = {}

    if request.method == "POST":
        form_data, errors = validar_historial_form(request.form)

        if not errors:
            try:
                historial_model.actualizar_observacion(
                    int(historial["id_historial_cita"]),
                    str(form_data["observacion"]),
                )
            except ValueError as error:
                flash(str(error), "error")
            except MySQLError:
                log_error_tecnico(logger, "Error editando historial desde cita")
                flash("No pudimos actualizar la observación. Intentá nuevamente.", "error")
            else:
                flash("Observación actualizada correctamente.", "success")
                return redirect(url_for("historial.index"))

    return render_template(
        "historial/form.html",
        page_title="Editar observación",
        page_kicker="Historial de Citas",
        cita=cita,
        form_data=form_data,
        errors=errors,
        action_url=url_for("historial.editar_desde_cita", id_cita=id_cita),
        submit_label="Actualizar observación",
    )


def _crear_indicadores(historiales: list[dict], rol: str | None = None) -> list[dict]:
    total = len(historiales)
    pacientes = {historial.get("paciente_dni") for historial in historiales if historial.get("paciente_dni")}
    especialidades = {historial.get("especialidad") for historial in historiales if historial.get("especialidad")}

    if rol == "MEDICO":
        fechas = [str(historial.get("fecha_atencion")) for historial in historiales if historial.get("fecha_atencion")]
        ultima_atencion = max(fechas) if fechas else "Sin registros"
        return [
            {"titulo": "Atenciones realizadas", "valor": total, "detalle": "Según filtro actual", "tono": "primary"},
            {"titulo": "Pacientes atendidos", "valor": len(pacientes), "detalle": "Pacientes únicos", "tono": "success"},
            {"titulo": "Última atención", "valor": ultima_atencion, "detalle": "Registro más reciente", "tono": "info"},
        ]

    medicos = {historial.get("medico") for historial in historiales if historial.get("medico")}
    return [
        {"titulo": "Atenciones registradas", "valor": total, "detalle": "Según filtro actual", "tono": "primary"},
        {"titulo": "Médicos", "valor": len(medicos), "detalle": "Con atenciones registradas", "tono": "success"},
        {"titulo": "Especialidades", "valor": len(especialidades), "detalle": "Cubiertas en el historial", "tono": "info"},
    ]


def _flash_error_mysql(error: MySQLError, mensaje_default: str) -> None:
    if getattr(error, "errno", None) == 1062:
        flash("La cita ya tiene un historial registrado.", "error")
        return

    flash(mensaje_default, "error")


def _obtener_id_medico_actual() -> int | None:
    usuario = get_current_user()
    if not usuario or usuario.get("rol") != "MEDICO":
        return None

    try:
        return medico_model.obtener_id_medico_por_usuario(int(usuario["id_usuario"]))
    except (MySQLError, KeyError, TypeError, ValueError):
        log_error_tecnico(logger, "Error obteniendo médico actual para historial")
        flash("No pudimos validar tu perfil médico. Intentá nuevamente.", "error")
        return None


def _obtener_id_usuario_actual() -> int | None:
    usuario = get_current_user()
    if not usuario:
        return None

    try:
        return int(usuario["id_usuario"])
    except (KeyError, TypeError, ValueError):
        return None
