from datetime import datetime
from typing import Any

from flask import Blueprint, flash, render_template, request
from mysql.connector import Error as MySQLError

from app.models.medico_model import MedicoModel
from app.models.reporte_model import ReporteModel
from app.utils.auth import roles_required
from app.utils.logger import get_logger, log_error_tecnico


reportes_bp = Blueprint("reportes", __name__)
logger = get_logger(__name__)
reporte_model = ReporteModel()
medico_model = MedicoModel()

ESTADOS_CITA = (
    "PENDIENTE",
    "CONFIRMADA",
    "CANCELADA",
    "ATENDIDA",
    "NO_ASISTIO",
    "REPROGRAMADA",
)


@reportes_bp.get("/reportes/citas")
@roles_required("ADMINISTRADOR")
def citas():
    filtros, form_data, mensajes = _leer_filtros()

    for mensaje in mensajes:
        flash(mensaje, "error")

    citas_reporte: list[dict[str, Any]] = []
    medicos: list[dict[str, Any]] = []

    try:
        citas_reporte = reporte_model.listar_citas(filtros)
        medicos = medico_model.listar()
    except MySQLError:
        log_error_tecnico(logger, "Error generando reporte de citas")
        flash("No pudimos generar el reporte de citas. Verificá la conexión a la base de datos.", "error")

    return render_template(
        "reportes/citas.html",
        page_title="Reporte de Citas",
        page_kicker="Reportes administrativos",
        citas=citas_reporte,
        medicos=medicos,
        estados=ESTADOS_CITA,
        filtros=form_data,
        indicadores=_crear_indicadores(citas_reporte),
        resumen_estados=_crear_resumen_por_estado(citas_reporte),
    )


def _leer_filtros() -> tuple[dict[str, Any], dict[str, str], list[str]]:
    estado = (request.args.get("estado") or "").strip().upper()
    id_medico_raw = (request.args.get("id_medico") or "").strip()
    fecha_inicio = (request.args.get("fecha_inicio") or "").strip()
    fecha_fin = (request.args.get("fecha_fin") or "").strip()

    filtros: dict[str, Any] = {}
    mensajes: list[str] = []

    if estado:
        if estado in ESTADOS_CITA:
            filtros["estado"] = estado
        else:
            mensajes.append("Seleccioná un estado de cita válido.")

    if id_medico_raw:
        try:
            filtros["id_medico"] = int(id_medico_raw)
        except ValueError:
            mensajes.append("Seleccioná un médico válido.")

    fecha_inicio_valida = _validar_fecha(fecha_inicio, "fecha de inicio", mensajes)
    fecha_fin_valida = _validar_fecha(fecha_fin, "fecha de fin", mensajes)

    if fecha_inicio_valida and fecha_fin_valida and fecha_inicio > fecha_fin:
        mensajes.append("La fecha de inicio no puede ser posterior a la fecha de fin.")
    else:
        if fecha_inicio_valida:
            filtros["fecha_inicio"] = fecha_inicio
        if fecha_fin_valida:
            filtros["fecha_fin"] = fecha_fin

    form_data = {
        "estado": estado if estado in ESTADOS_CITA else "",
        "id_medico": id_medico_raw if id_medico_raw.isdigit() else "",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return filtros, form_data, mensajes


def _validar_fecha(valor: str, etiqueta: str, mensajes: list[str]) -> bool:
    if not valor:
        return False

    try:
        datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        mensajes.append(f"La {etiqueta} debe usar el formato AAAA-MM-DD.")
        return False

    return True


def _crear_indicadores(citas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = len(citas)
    activas = sum(1 for cita in citas if cita.get("estado") in {"PENDIENTE", "CONFIRMADA"})
    finalizadas = sum(1 for cita in citas if cita.get("estado") in {"ATENDIDA", "NO_ASISTIO"})

    return [
        {"titulo": "Total filtrado", "valor": total, "detalle": "Citas según filtros", "tono": "primary"},
        {"titulo": "Activas", "valor": activas, "detalle": "Pendientes o confirmadas", "tono": "warning"},
        {"titulo": "Finalizadas", "valor": finalizadas, "detalle": "Atendidas o no asistió", "tono": "success"},
    ]


def _crear_resumen_por_estado(citas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_por_estado = {estado: 0 for estado in ESTADOS_CITA}

    for cita in citas:
        estado = cita.get("estado")
        if estado in total_por_estado:
            total_por_estado[estado] += 1

    return [{"estado": estado, "total": total} for estado, total in total_por_estado.items()]
