from flask import Blueprint, render_template

from app.utils.auth import login_required


home_bp = Blueprint("home", __name__)


@home_bp.get("/")
@login_required
def index():
    resumen = [
        {
            "titulo": "Citas de hoy",
            "valor": 24,
            "detalle": "6 pendientes de confirmación",
            "tono": "primary",
        },
        {
            "titulo": "Pacientes activos",
            "valor": 184,
            "detalle": "Datos temporales hasta conectar modelo",
            "tono": "success",
        },
        {
            "titulo": "Médicos disponibles",
            "valor": 12,
            "detalle": "4 especialidades con atención",
            "tono": "info",
        },
        {
            "titulo": "Citas canceladas",
            "valor": 3,
            "detalle": "Últimas 24 horas",
            "tono": "warning",
        },
    ]

    proximas_citas = [
        {
            "hora": "09:00",
            "paciente": "María Gonzales",
            "medico": "Dra. Ana Torres",
            "especialidad": "Medicina General",
            "estado": "CONFIRMADA",
        },
        {
            "hora": "10:30",
            "paciente": "Carlos Ramírez",
            "medico": "Dr. Luis Mendoza",
            "especialidad": "Cardiología",
            "estado": "PENDIENTE",
        },
        {
            "hora": "12:00",
            "paciente": "Lucía Herrera",
            "medico": "Dra. Sofía Rojas",
            "especialidad": "Pediatría",
            "estado": "CONFIRMADA",
        },
    ]

    actividad_reciente = [
        "Se registró una nueva cita para Medicina General.",
        "Recepción confirmó una cita pendiente.",
        "Historial actualizado para una atención finalizada.",
    ]

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

    alertas_admin = [
        "2 médicos sin horario activo configurado.",
        "5 pacientes requieren actualización de datos de contacto.",
        "3 citas pendientes siguen sin notificación registrada.",
    ]

    return render_template(
        "home/index.html",
        page_title="Panel de control",
        page_kicker="Resumen operativo",
        resumen=resumen,
        proximas_citas=proximas_citas,
        actividad_reciente=actividad_reciente,
        modulos_admin=modulos_admin,
        alertas_admin=alertas_admin,
    )
