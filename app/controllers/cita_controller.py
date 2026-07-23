import smtplib

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError

from app.models.cita_model import CitaModel
from app.models.historial_cita_model import HistorialCitaModel
from app.models.horario_model import HorarioModel
from app.models.medico_model import MedicoModel
from app.models.paciente_model import PacienteModel
from app.services.mail_service import MailConfigurationError, send_appointment_notification
from app.utils.auth import get_current_user, roles_required
from app.utils.logger import get_logger, log_error_tecnico
from app.utils.validators import (
    validar_cancelacion_cita_form,
    validar_historial_form,
    validar_programacion_cita_form,
    validar_reprogramacion_cita_form,
)


citas_bp = Blueprint("citas", __name__)
logger = get_logger(__name__)
cita_model = CitaModel()
paciente_model = PacienteModel()
medico_model = MedicoModel()
horario_model = HorarioModel()
historial_model = HistorialCitaModel()


@citas_bp.get("/citas")
@roles_required("ADMINISTRADOR", "RECEPCIONISTA", "MEDICO")
def index():
    busqueda = (request.args.get("q") or "").strip()
    citas = []
    usuario = get_current_user()

    try:
        if usuario and usuario.get("rol") == "MEDICO":
            id_medico = _obtener_id_medico_actual()
            citas = cita_model.listar_por_medico(id_medico, busqueda or None) if id_medico else []
        else:
            citas = cita_model.listar(busqueda or None)
    except MySQLError:
        log_error_tecnico(logger, "Error listando citas")
        flash("No pudimos cargar las citas. Verificá la conexión a la base de datos.", "error")

    return render_template(
        "citas/index.html",
        page_title="Citas médicas",
        page_kicker="Agenda médica",
        citas=citas,
        indicadores=_crear_indicadores(citas),
        busqueda=busqueda,
    )


@citas_bp.route("/citas/programar", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def programar():
    form_data: dict = {}
    errors: dict[str, str] = {}

    if request.method == "POST":
        form_data, errors = validar_programacion_cita_form(request.form)

        if not errors:
            datos = dict(form_data)
            datos["id_recepcionista"] = _obtener_id_recepcionista_actual()

            try:
                id_cita = cita_model.programar_cita(datos)
            except ValueError as error:
                flash(str(error), "error")
            except MySQLError as error:
                log_error_tecnico(logger, "Error programando cita")
                _flash_error_mysql(error, "No pudimos programar la cita. Revisá los datos e intentá nuevamente.")
            else:
                flash("Cita programada correctamente.", "success")
                return redirect(url_for("citas.index", id_cita=id_cita))
    else:
        form_data = {
            "id_paciente": request.args.get("id_paciente", type=int),
            "id_medico": request.args.get("id_medico", type=int),
            "fecha": request.args.get("fecha", ""),
            "hora": request.args.get("hora", ""),
            "motivo_consulta": "",
        }

    pacientes, medicos, horarios_disponibles = _cargar_datos_programacion(form_data.get("id_medico"))

    return render_template(
        "citas/programar.html",
        page_title="Programar cita",
        page_kicker="Agenda médica",
        pacientes=pacientes,
        medicos=medicos,
        horarios_disponibles=horarios_disponibles,
        form_data=form_data,
        errors=errors,
    )


@citas_bp.post("/citas/<int:id_cita>/cancelar")
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def cancelar(id_cita: int):
    form_data, errors = validar_cancelacion_cita_form(request.form)

    if errors:
        for mensaje in errors.values():
            flash(mensaje, "error")
        return redirect(url_for("citas.index"))

    try:
        cita_model.cancelar_cita(id_cita, form_data["motivo_cancelacion"], _obtener_id_usuario_actual())
    except ValueError as error:
        flash(str(error), "error")
    except MySQLError:
        log_error_tecnico(logger, "Error cancelando cita")
        flash("No pudimos cancelar la cita. Intentá nuevamente.", "error")
    else:
        flash("Cita cancelada correctamente.", "success")

    return redirect(url_for("citas.index"))


@citas_bp.post("/citas/<int:id_cita>/confirmar")
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def confirmar(id_cita: int):
    try:
        cita_model.confirmar_cita(id_cita, _obtener_id_usuario_actual())
    except ValueError as error:
        flash(str(error), "error")
    except MySQLError:
        log_error_tecnico(logger, "Error confirmando cita")
        flash("No pudimos confirmar la cita. Intentá nuevamente.", "error")
    else:
        flash("Cita confirmada correctamente.", "success")

    return redirect(url_for("citas.index"))


@citas_bp.post("/citas/<int:id_cita>/notificar")
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def notificar(id_cita: int):
    try:
        cita = cita_model.obtener_por_id(id_cita)
        if not cita:
            abort(404)
        if not cita_model.es_notificable(cita):
            flash("Solo se pueden notificar citas pendientes o confirmadas.", "error")
            return redirect(url_for("citas.index"))
        send_appointment_notification(cita)
        cita_model.marcar_notificada(id_cita, _obtener_id_usuario_actual())
    except MailConfigurationError as error:
        try:
            cita_model.registrar_notificacion_fallida(id_cita, str(error), _obtener_id_usuario_actual())
        except MySQLError:
            log_error_tecnico(logger, "Error registrando fallo de notificación")
        flash(str(error), "error")
    except (OSError, smtplib.SMTPException) as error:
        log_error_tecnico(logger, "Error enviando correo de notificación")
        try:
            cita_model.registrar_notificacion_fallida(id_cita, "No se pudo enviar el correo SMTP.", _obtener_id_usuario_actual())
        except MySQLError:
            log_error_tecnico(logger, "Error registrando fallo de notificación")
        flash("No pudimos enviar el correo al paciente. La cita no fue marcada como notificada.", "error")
    except ValueError as error:
        flash(str(error), "error")
    except MySQLError:
        log_error_tecnico(logger, "Error notificando cita")
        flash("No pudimos procesar la notificación del paciente.", "error")
    else:
        flash("Correo enviado y paciente marcado como notificado.", "success")

    return redirect(url_for("citas.index"))


@citas_bp.route("/citas/<int:id_cita>/reprogramar", methods=["GET", "POST"])
@roles_required("ADMINISTRADOR", "RECEPCIONISTA")
def reprogramar(id_cita: int):
    try:
        cita = cita_model.obtener_por_id(id_cita)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo cita para reprogramar")
        flash("No pudimos cargar la cita solicitada.", "error")
        return redirect(url_for("citas.index"))

    if not cita:
        abort(404)

    if cita["estado"] not in {"PENDIENTE", "CONFIRMADA"}:
        flash("Solo se pueden reprogramar citas pendientes o confirmadas.", "error")
        return redirect(url_for("citas.index"))

    errors: dict[str, str] = {}
    form_data: dict = {
        "id_medico": request.args.get("id_medico", type=int) or cita["id_medico"],
        "fecha": request.args.get("fecha", ""),
        "hora": request.args.get("hora", ""),
        "motivo_consulta": request.args.get("motivo_consulta", cita.get("motivo_consulta") or ""),
    }

    if request.method == "POST":
        form_data, errors = validar_reprogramacion_cita_form(request.form)

        if not errors:
            datos = dict(form_data)
            datos["id_recepcionista"] = _obtener_id_recepcionista_actual()

            try:
                nueva_cita = cita_model.reprogramar_cita(id_cita, datos, _obtener_id_usuario_actual())
            except ValueError as error:
                flash(str(error), "error")
            except MySQLError as error:
                log_error_tecnico(logger, "Error reprogramando cita")
                _flash_error_mysql(error, "No pudimos reprogramar la cita. Intentá nuevamente.")
            else:
                flash("Cita reprogramada correctamente.", "success")
                return redirect(url_for("citas.index", id_cita=nueva_cita))

    pacientes, medicos, horarios_disponibles = _cargar_datos_programacion(form_data.get("id_medico"))

    return render_template(
        "citas/reprogramar.html",
        page_title="Reprogramar cita",
        page_kicker="Agenda médica",
        cita=cita,
        medicos=medicos,
        horarios_disponibles=horarios_disponibles,
        form_data=form_data,
        errors=errors,
    )


@citas_bp.route("/citas/<int:id_cita>/seguimiento", methods=["GET", "POST"])
@roles_required("MEDICO")
def crear_seguimiento(id_cita: int):
    id_medico = _obtener_id_medico_actual()
    if not id_medico:
        return redirect(url_for("citas.index"))

    try:
        cita = cita_model.obtener_por_id_y_medico(id_cita, id_medico)
    except MySQLError:
        log_error_tecnico(logger, "Error obteniendo cita para seguimiento")
        flash("No pudimos cargar la cita solicitada.", "error")
        return redirect(url_for("citas.index"))

    if not cita:
        abort(404)
    if cita["estado"] not in {"PENDIENTE", "CONFIRMADA", "ATENDIDA"}:
        flash("Solo podés crear seguimiento desde una cita activa o atendida.", "error")
        return redirect(url_for("citas.index"))

    errors: dict[str, str] = {}
    form_data: dict = {
        "id_medico": id_medico,
        "fecha": request.args.get("fecha", ""),
        "hora": request.args.get("hora", ""),
        "motivo_consulta": request.args.get("motivo_consulta", "Seguimiento médico"),
    }

    if request.method == "POST":
        form_data, errors = validar_reprogramacion_cita_form(request.form)
        form_data["id_medico"] = id_medico

        if not errors:
            try:
                nueva_cita = cita_model.crear_seguimiento(id_cita, form_data, _obtener_id_usuario_actual())
            except ValueError as error:
                flash(str(error), "error")
            except MySQLError as error:
                log_error_tecnico(logger, "Error creando seguimiento")
                _flash_error_mysql(error, "No pudimos crear la cita de seguimiento. Intentá nuevamente.")
            else:
                flash("Cita de seguimiento creada correctamente.", "success")
                return redirect(url_for("citas.index", id_cita=nueva_cita))

    _, _, horarios_disponibles = _cargar_datos_programacion(id_medico)

    return render_template(
        "citas/seguimiento.html",
        page_title="Crear seguimiento",
        page_kicker="Agenda médica",
        cita=cita,
        horarios_disponibles=horarios_disponibles,
        form_data=form_data,
        errors=errors,
    )


@citas_bp.post("/citas/<int:id_cita>/atender")
@roles_required("ADMINISTRADOR", "MEDICO")
def atender(id_cita: int):
    if not _puede_medico_operar_cita(id_cita):
        return redirect(url_for("citas.index"))

    form_data, errors = validar_historial_form(request.form)

    if errors:
        for mensaje in errors.values():
            flash(mensaje, "error")
        return redirect(url_for("historial.nuevo_desde_cita", id_cita=id_cita))

    try:
        historial_model.atender_y_crear_desde_cita(id_cita, str(form_data["observacion"]), _obtener_id_usuario_actual())
    except ValueError as error:
        flash(str(error), "error")
    except MySQLError as error:
        log_error_tecnico(logger, "Error atendiendo cita")
        _flash_error_mysql(error, "No pudimos registrar la atención. Intentá nuevamente.")
    else:
        flash("Atención registrada e historial creado correctamente.", "success")
        return redirect(url_for("historial.index"))

    return redirect(url_for("citas.index"))


@citas_bp.post("/citas/<int:id_cita>/no-asistio")
@roles_required("ADMINISTRADOR", "MEDICO")
def marcar_no_asistio(id_cita: int):
    if not _puede_medico_operar_cita(id_cita):
        return redirect(url_for("citas.index"))

    try:
        cita_model.marcar_no_asistio(id_cita, _obtener_id_usuario_actual())
    except ValueError as error:
        flash(str(error), "error")
    except MySQLError:
        log_error_tecnico(logger, "Error marcando cita como no asistida")
        flash("No pudimos actualizar la cita.", "error")
    else:
        flash("Cita marcada como no asistida.", "success")

    return redirect(url_for("citas.index"))


def _cargar_datos_programacion(id_medico: int | str | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    pacientes: list[dict] = []
    medicos: list[dict] = []
    horarios_disponibles: list[dict] = []

    try:
        pacientes = paciente_model.listar()
        medicos = medico_model.listar()
        id_medico_int = int(id_medico) if id_medico else None
        if id_medico_int:
            horarios_disponibles = [
                _normalizar_horario(horario)
                for horario in horario_model.listar_por_medico(id_medico_int)
                if horario.get("estado") == "DISPONIBLE"
            ]
        else:
            horarios_disponibles = [_normalizar_horario(horario) for horario in cita_model.listar_horarios_disponibles()]
    except (MySQLError, ValueError):
        log_error_tecnico(logger, "Error cargando datos de programación")
        flash("No pudimos cargar pacientes, médicos u horarios disponibles.", "error")

    return pacientes, medicos, horarios_disponibles


def _normalizar_horario(horario: dict) -> dict:
    horario_normalizado = dict(horario)
    horario_normalizado["hora_inicio_form"] = horario.get("hora_inicio_form") or _hora_hhmm(horario.get("hora_inicio"))
    horario_normalizado["hora_fin_form"] = horario.get("hora_fin_form") or _hora_hhmm(horario.get("hora_fin"))
    return horario_normalizado


def _hora_hhmm(valor: object) -> str:
    if valor is None:
        return ""

    partes = str(valor).split(":")
    if len(partes) < 2:
        return str(valor)

    try:
        return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
    except ValueError:
        return str(valor)


def _obtener_id_recepcionista_actual() -> int | None:
    usuario = get_current_user()
    if not usuario or usuario.get("rol") != "RECEPCIONISTA":
        return None

    try:
        return cita_model.obtener_id_recepcionista_por_usuario(int(usuario["id_usuario"]))
    except (MySQLError, KeyError, TypeError, ValueError):
        log_error_tecnico(logger, "Error obteniendo recepcionista actual")
        return None


def _obtener_id_usuario_actual() -> int | None:
    usuario = get_current_user()
    if not usuario:
        return None

    try:
        return int(usuario["id_usuario"])
    except (KeyError, TypeError, ValueError):
        return None


def _obtener_id_medico_actual() -> int | None:
    usuario = get_current_user()
    if not usuario or usuario.get("rol") != "MEDICO":
        return None

    try:
        return medico_model.obtener_id_medico_por_usuario(int(usuario["id_usuario"]))
    except (MySQLError, KeyError, TypeError, ValueError):
        log_error_tecnico(logger, "Error obteniendo médico actual")
        flash("No pudimos validar tu perfil médico. Intentá nuevamente.", "error")
        return None


def _puede_medico_operar_cita(id_cita: int) -> bool:
    usuario = get_current_user()
    if not usuario or usuario.get("rol") != "MEDICO":
        return True

    id_medico = _obtener_id_medico_actual()
    if not id_medico:
        return False

    try:
        cita = cita_model.obtener_por_id_y_medico(id_cita, id_medico)
    except MySQLError:
        log_error_tecnico(logger, "Error validando pertenencia de cita")
        flash("No pudimos validar la cita solicitada. Intentá nuevamente.", "error")
        return False

    if not cita:
        flash("No tenés acceso a esa cita médica.", "error")
        return False

    return True


def _crear_indicadores(citas: list[dict]) -> list[dict]:
    total = len(citas)
    pendientes = sum(1 for cita in citas if cita.get("estado") == "PENDIENTE")
    confirmadas = sum(1 for cita in citas if cita.get("estado") == "CONFIRMADA")
    activas = pendientes + confirmadas
    sin_notificar = sum(1 for cita in citas if cita.get("estado") in {"PENDIENTE", "CONFIRMADA"} and not cita.get("notificado"))

    return [
        {"titulo": "Citas listadas", "valor": total, "detalle": "Según filtro actual", "tono": "primary"},
        {"titulo": "Activas", "valor": activas, "detalle": f"{pendientes} pendientes / {confirmadas} confirmadas", "tono": "warning"},
        {"titulo": "Sin notificar", "valor": sin_notificar, "detalle": "Pendientes de aviso al paciente", "tono": "info"},
    ]


def _flash_error_mysql(error: MySQLError, mensaje_default: str) -> None:
    if getattr(error, "errno", None) == 1062:
        flash("Ya existe una cita o historial con esos datos.", "error")
        return

    flash(mensaje_default, "error")
