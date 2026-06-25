import smtplib

from mysql.connector import Error as MySQLError

from app.models.cita_model import CitaModel
from app.services.mail_service import MailConfigurationError, send_appointment_notification
from app.utils.logger import get_logger, log_error_tecnico


logger = get_logger(__name__)


def send_pending_reminders() -> int:
    """Send reminders for upcoming appointments without duplicating notified citas."""
    cita_model = CitaModel()
    sent = 0
    failed = 0
    for cita in cita_model.listar_pendientes_recordatorio():
        id_cita = _obtener_id_cita(cita)

        try:
            if id_cita is None:
                raise ValueError("La cita no tiene un id válido.")
            send_appointment_notification(cita)
            cita_model.marcar_notificada(id_cita)
        except MailConfigurationError as error:
            failed += 1
            _registrar_recordatorio_fallido(cita_model, id_cita, str(error))
            logger.warning("Recordatorio no enviado por configuración: %s", error)
            continue
        except (OSError, smtplib.SMTPException):
            failed += 1
            _registrar_recordatorio_fallido(cita_model, id_cita, "No se pudo enviar el correo SMTP.")
            log_error_tecnico(logger, "Error enviando recordatorio SMTP")
            continue
        except (MySQLError, ValueError):
            failed += 1
            _registrar_recordatorio_fallido(cita_model, id_cita, "No se pudo marcar o registrar el recordatorio.")
            log_error_tecnico(logger, "Error procesando recordatorio de cita")
            continue
        except Exception:
            failed += 1
            _registrar_recordatorio_fallido(cita_model, id_cita, "Error inesperado enviando recordatorio.")
            log_error_tecnico(logger, "Error inesperado enviando recordatorio")
            continue

        sent += 1
    logger.info("Recordatorios procesados: enviados=%s fallidos=%s", sent, failed)
    return sent


def _obtener_id_cita(cita: dict) -> int | None:
    try:
        return int(cita["id_cita"])
    except (KeyError, TypeError, ValueError):
        return None


def _registrar_recordatorio_fallido(cita_model: CitaModel, id_cita: int | None, detalle: str) -> None:
    if id_cita is None:
        return

    try:
        cita_model.registrar_notificacion_fallida(id_cita, detalle)
    except (MySQLError, ValueError):
        log_error_tecnico(logger, "Error registrando fallo de recordatorio")
