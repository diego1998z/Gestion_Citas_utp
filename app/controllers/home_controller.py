from flask import Blueprint, flash, render_template, url_for
from mysql.connector import Error as MySQLError

from app.models.cita_model import CitaModel
from app.models.medico_model import MedicoModel
from app.models.paciente_model import PacienteModel
from app.utils.auth import get_current_user, login_required
from app.utils.logger import get_logger, log_error_tecnico


home_bp = Blueprint("home", __name__)
logger = get_logger(__name__)
cita_model = CitaModel()
paciente_model = PacienteModel()
medico_model = MedicoModel()


@home_bp.get("/")
@login_required
def index():
    usuario = get_current_user()
    if usuario and usuario.get("rol") == "MEDICO":
        dashboard = _crear_dashboard_medico(usuario)
    else:
        dashboard = _crear_dashboard_general()

    return render_template(
        "home/index.html",
        page_title="Panel de control",
        page_kicker="Resumen operativo",
        **dashboard,
    )


def _crear_dashboard_medico(usuario: dict) -> dict:
    citas: list[dict] = []
    pacientes: list[dict] = []

    try:
        id_medico = medico_model.obtener_id_medico_por_usuario(int(usuario["id_usuario"]))
        if not id_medico:
            flash("No pudimos encontrar tu perfil médico asociado.", "error")
        else:
            citas = cita_model.listar_por_medico(id_medico)
            pacientes = paciente_model.listar_por_medico(id_medico)
    except (MySQLError, KeyError, TypeError, ValueError):
        log_error_tecnico(logger, "Error cargando dashboard médico")
        flash("No pudimos cargar tu panel médico. Mostramos datos vacíos para que puedas seguir navegando.", "error")

    pendientes = sum(1 for cita in citas if cita.get("estado") == "PENDIENTE")
    confirmadas = sum(1 for cita in citas if cita.get("estado") == "CONFIRMADA")
    atendidas = sum(1 for cita in citas if cita.get("estado") == "ATENDIDA")
    activas = pendientes + confirmadas

    proximas_citas = sorted(
        [cita for cita in citas if cita.get("estado") in {"PENDIENTE", "CONFIRMADA"}],
        key=lambda cita: (str(cita.get("fecha") or ""), str(cita.get("hora") or "")),
    )[:5]

    return {
        "hero_description": "Vista operativa de tus citas, pacientes vinculados e historial de atención.",
        "hero_action_label": None,
        "hero_action_url": "#",
        "agenda_url": url_for("citas.index"),
        "agenda_link_label": "Ver mis citas",
        "resumen": [
            {
                "titulo": "Mis citas activas",
                "valor": activas,
                "detalle": f"{pendientes} pendientes / {confirmadas} confirmadas",
                "tono": "primary",
            },
            {
                "titulo": "Mis pacientes",
                "valor": len(pacientes),
                "detalle": "Pacientes únicos con citas vinculadas",
                "tono": "success",
            },
            {
                "titulo": "Atenciones registradas",
                "valor": atendidas,
                "detalle": "Citas marcadas como atendidas",
                "tono": "info",
            },
            {
                "titulo": "Total de citas",
                "valor": len(citas),
                "detalle": "Histórico asociado a tu perfil",
                "tono": "warning",
            },
        ],
        "proximas_citas": proximas_citas,
        "actividad_reciente": _crear_actividad_medico(citas, pacientes),
        "modulos_admin": [],
        "alertas_admin": [],
    }


def _crear_dashboard_general() -> dict:
    try:
        datos = cita_model.obtener_dashboard_operativo()
    except MySQLError:
        log_error_tecnico(logger, "Error cargando dashboard operativo")
        flash("No pudimos cargar el resumen operativo desde la base de datos.", "error")
        datos = {
            "resumen_citas": {},
            "total_pacientes": 0,
            "disponibilidad": {},
            "proximas_citas": [],
            "actividad": [],
            "medicos_sin_horario": 0,
            "pacientes_contacto_incompleto": 0,
        }

    resumen_citas = datos.get("resumen_citas") or {}
    disponibilidad = datos.get("disponibilidad") or {}

    resumen = [
        {
            "titulo": "Citas de hoy",
            "valor": resumen_citas.get("citas_hoy", 0),
            "detalle": f"{resumen_citas.get('pendientes_hoy', 0)} pendientes hoy",
            "tono": "primary",
        },
        {
            "titulo": "Pacientes activos",
            "valor": datos.get("total_pacientes", 0),
            "detalle": "Pacientes registrados en el sistema",
            "tono": "success",
        },
        {
            "titulo": "Médicos disponibles",
            "valor": disponibilidad.get("medicos_disponibles", 0),
            "detalle": f"{disponibilidad.get('especialidades_disponibles', 0)} especialidades con horario vigente",
            "tono": "info",
        },
        {
            "titulo": "Citas canceladas",
            "valor": resumen_citas.get("canceladas_24h", 0),
            "detalle": "Desde ayer hasta hoy",
            "tono": "warning",
        },
    ]

    proximas_citas = datos.get("proximas_citas") or []
    actividad_reciente = [_formatear_actividad_general(evento) for evento in datos.get("actividad") or []]

    modulos_admin = [
        {
            "icono": "👥",
            "titulo": "Pacientes",
            "descripcion": "Alta, actualización y consulta de pacientes registrados.",
            "url": "/pacientes",
        },
        {
            "icono": "🩺",
            "titulo": "Médicos",
            "descripcion": "Control de especialidades, personal médico y disponibilidad.",
            "url": "/medicos",
        },
        {
            "icono": "📅",
            "titulo": "Programación de citas",
            "descripcion": "Agenda operativa para recepción y administración.",
            "url": "/citas/programar",
        },
    ]

    alertas_admin = _crear_alertas_admin(datos)

    return {
        "hero_description": "Vista operativa para monitorear citas, disponibilidad médica e historial de atención con datos registrados en el sistema.",
        "hero_action_label": "Nueva cita",
        "hero_action_url": url_for("citas.programar"),
        "agenda_url": url_for("citas.index"),
        "agenda_link_label": "Ver agenda",
        "resumen": resumen,
        "proximas_citas": proximas_citas,
        "actividad_reciente": actividad_reciente,
        "modulos_admin": modulos_admin,
        "alertas_admin": alertas_admin,
    }


def _formatear_actividad_general(evento: dict) -> str:
    tipo = str(evento.get("tipo_evento") or "Evento").replace("_", " ").title()
    paciente = evento.get("paciente") or "paciente registrado"
    actor = evento.get("actor") or "Sistema"
    return f"{tipo} para {paciente}. Registrado por {actor}."


def _crear_alertas_admin(datos: dict) -> list[str]:
    resumen_citas = datos.get("resumen_citas") or {}
    alertas = []

    medicos_sin_horario = int(datos.get("medicos_sin_horario") or 0)
    if medicos_sin_horario:
        alertas.append(f"{medicos_sin_horario} médico(s) activo(s) sin horario disponible vigente.")

    pacientes_contacto_incompleto = int(datos.get("pacientes_contacto_incompleto") or 0)
    if pacientes_contacto_incompleto:
        alertas.append(f"{pacientes_contacto_incompleto} paciente(s) con datos de contacto incompletos.")

    pendientes_notificacion = int(resumen_citas.get("pendientes_notificacion") or 0)
    if pendientes_notificacion:
        alertas.append(f"{pendientes_notificacion} cita(s) activa(s) sin notificación registrada.")

    return alertas


def _crear_actividad_medico(citas: list[dict], pacientes: list[dict]) -> list[str]:
    if not citas and not pacientes:
        return ["No hay actividad médica vinculada por ahora."]

    pendientes = sum(1 for cita in citas if cita.get("estado") == "PENDIENTE")
    confirmadas = sum(1 for cita in citas if cita.get("estado") == "CONFIRMADA")
    atendidas = sum(1 for cita in citas if cita.get("estado") == "ATENDIDA")

    return [
        f"Tenés {pendientes} cita(s) pendiente(s) de atención o confirmación.",
        f"Tenés {confirmadas} cita(s) confirmada(s) en tu agenda.",
        f"Registraste {atendidas} atención(es) en tus citas vinculadas.",
    ]
