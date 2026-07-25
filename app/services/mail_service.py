import json
import smtplib
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.settings import Config


class MailConfigurationError(RuntimeError):
    pass


class MailDeliveryError(RuntimeError):
    pass


def send_appointment_notification(cita: dict) -> None:
    destinatario = cita.get("paciente_email")
    if not destinatario:
        raise MailConfigurationError("El paciente no tiene correo registrado.")

    subject = "Recordatorio de cita médica"
    text_content = _build_text_content(cita)
    html_content = _build_html_content(cita)

    if Config.EMAIL_PROVIDER == "brevo":
        _send_with_brevo(destinatario, subject, text_content, html_content)
        return

    if Config.EMAIL_PROVIDER == "smtp":
        _send_with_smtp(destinatario, subject, text_content)
        return

    raise MailConfigurationError("Proveedor de correo no soportado. Usá EMAIL_PROVIDER=smtp o EMAIL_PROVIDER=brevo.")


def _build_text_content(cita: dict) -> str:
    return (
        "Estimado/a paciente,\n\n"
        f"Le recordamos su cita médica para el {cita.get('fecha')} a las {cita.get('hora')} "
        f"con {cita.get('medico')}.\n\n"
        "Por favor, acérquese puntualmente.\n"
    )


def _build_html_content(cita: dict) -> str:
    return (
        "<p>Estimado/a paciente,</p>"
        "<p>Le recordamos su cita médica para el "
        f"<strong>{cita.get('fecha')}</strong> a las <strong>{cita.get('hora')}</strong> "
        f"con <strong>{cita.get('medico')}</strong>.</p>"
        "<p>Por favor, acérquese puntualmente.</p>"
    )


def _send_with_smtp(destinatario: str, subject: str, text_content: str) -> None:
    if not Config.SMTP_HOST or not Config.SMTP_FROM:
        raise MailConfigurationError("SMTP no está configurado.")

    mensaje = EmailMessage()
    mensaje["Subject"] = subject
    mensaje["From"] = Config.SMTP_FROM
    mensaje["To"] = destinatario
    mensaje.set_content(text_content)

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as smtp:
        if Config.SMTP_USE_TLS:
            smtp.starttls()
        if Config.SMTP_USER:
            smtp.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        smtp.send_message(mensaje)


def _send_with_brevo(destinatario: str, subject: str, text_content: str, html_content: str) -> None:
    if not Config.BREVO_API_KEY:
        raise MailConfigurationError("BREVO_API_KEY no está configurada.")
    if not Config.BREVO_FROM_EMAIL:
        raise MailConfigurationError("BREVO_FROM_EMAIL no está configurado.")

    payload = {
        "sender": {
            "email": Config.BREVO_FROM_EMAIL,
            "name": Config.BREVO_FROM_NAME,
        },
        "to": [{"email": destinatario}],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    request = Request(
        Config.BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": Config.BREVO_API_KEY,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status >= 400:
                raise MailDeliveryError(f"Brevo respondió con estado HTTP {response.status}.")
    except HTTPError as error:
        detail = _read_error_detail(error)
        raise MailDeliveryError(f"Brevo respondió con estado HTTP {error.code}. {detail}") from error
    except URLError as error:
        raise MailDeliveryError("No se pudo conectar con Brevo por HTTPS.") from error


def _read_error_detail(error: HTTPError) -> str:
    try:
        raw_body = error.read().decode("utf-8", errors="replace")
    except Exception:
        return ""

    if not raw_body:
        return ""

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return ""

    message = body.get("message")
    code = body.get("code")
    if message and code:
        return f"Código: {code}. Mensaje: {message}"
    if message:
        return f"Mensaje: {message}"
    return ""
