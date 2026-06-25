import smtplib
from email.message import EmailMessage

from config.settings import Config


class MailConfigurationError(RuntimeError):
    pass


def send_appointment_notification(cita: dict) -> None:
    if not Config.SMTP_HOST or not Config.SMTP_FROM:
        raise MailConfigurationError("SMTP no está configurado.")

    destinatario = cita.get("paciente_email")
    if not destinatario:
        raise MailConfigurationError("El paciente no tiene correo registrado.")

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recordatorio de cita médica"
    mensaje["From"] = Config.SMTP_FROM
    mensaje["To"] = destinatario
    mensaje.set_content(
        "Estimado/a paciente,\n\n"
        f"Le recordamos su cita médica para el {cita.get('fecha')} a las {cita.get('hora')} "
        f"con {cita.get('medico')}.\n\n"
        "Por favor, acérquese puntualmente.\n"
    )

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as smtp:
        if Config.SMTP_USE_TLS:
            smtp.starttls()
        if Config.SMTP_USER:
            smtp.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        smtp.send_message(mensaje)
