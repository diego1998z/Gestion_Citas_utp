from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError

from app.models.cita_model import CitaModel
from app.models.historial_cita_model import HistorialCitaModel
from app.utils.auth import roles_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.validators import validar_historial_form


historial_bp = Blueprint("historial", __name__)
logger = get_logger(__name__)
historial_model = HistorialCitaModel()
cita_model = CitaModel()


@historial_bp.get("/historial")
@roles_required("ADMINISTRADOR", "MEDICO", "RECEPCIONISTA")
def index():
    busqueda = (request.args.get("q") or "").strip()
    historiales = []

    try:
        historiales = historial_model.listar(busqueda or None)
    except MySQLError:
        log_error_tecnico(logger, "Error listando historial")
        flash("No pudimos cargar el historial de citas.", "error")

    return render_template(
        "historial/index.html",
        page_title="Historial de Citas",
        page_kicker="Registro de atenciones",
        historiales=historiales,
        indicadores=_crear_indicadores(historiales),
        busqueda=busqueda,
    )


@historial_bp.route("/historial/cita/<int:id_cita>/nuevo", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "MEDICO")
def nuevo_desde_cita(id_cita: int):
    try:
        cita = cita_model.obtener_por_id(id_cita)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo cita para historial")
        flash("No pudimos cargar la cita solicitada.", "error")
        return redirect(url_for("citas.index"))

    if not cita:
        abort(404)

    if cita.get("tiene_historial"):
        flash("La cita ya tiene un historial registrado.", "error")
        return redirect(url_for("historial.index"))

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
                    historial_model.atender_y_crear_desde_cita(id_cita, str(form_data["observacion"]))
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
    )


def _crear_indicadores(historiales: list[dict]) -> list[dict]:
    total = len(historiales)
    medicos = {historial.get("medico") for historial in historiales if historial.get("medico")}
    especialidades = {historial.get("especialidad") for historial in historiales if historial.get("especialidad")}

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
