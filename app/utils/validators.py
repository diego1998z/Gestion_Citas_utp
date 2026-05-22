from datetime import datetime

from werkzeug.datastructures import MultiDict


MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 128
MAX_NOMBRE_LENGTH = 100
MAX_EMAIL_LENGTH = 120
MAX_TELEFONO_LENGTH = 20
ESTADOS_USUARIO = {"ACTIVO", "INACTIVO"}
ESTADOS_HORARIO = {"DISPONIBLE", "NO_DISPONIBLE"}


def validar_login_form(form: MultiDict) -> tuple[dict[str, str], dict[str, str]]:
    username = (form.get("username") or "").strip()
    password = form.get("password") or ""

    datos = {
        "username": username,
        "password": password,
    }
    errores: dict[str, str] = {}

    if not username:
        errores["username"] = "Ingresá tu usuario."
    elif len(username) > MAX_USERNAME_LENGTH:
        errores["username"] = f"El usuario no puede superar {MAX_USERNAME_LENGTH} caracteres."

    if not password:
        errores["password"] = "Ingresá tu contraseña."
    elif len(password) > MAX_PASSWORD_LENGTH:
        errores["password"] = f"La contraseña no puede superar {MAX_PASSWORD_LENGTH} caracteres."

    return datos, errores


def _normalizar_texto(valor: str | None) -> str:
    return (valor or "").strip()


def _normalizar_opcional(valor: str | None) -> str | None:
    texto = _normalizar_texto(valor)
    return texto or None


def _validar_email(email: str | None, errores: dict[str, str]) -> None:
    if not email:
        return

    if len(email) > MAX_EMAIL_LENGTH:
        errores["email"] = f"El correo no puede superar {MAX_EMAIL_LENGTH} caracteres."
    elif "@" not in email or "." not in email.rsplit("@", maxsplit=1)[-1]:
        errores["email"] = "Ingresá un correo válido."


def _validar_fecha(fecha: str | None, campo: str, errores: dict[str, str]) -> str | None:
    if not fecha:
        return None

    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        errores[campo] = "Ingresá una fecha válida."
        return fecha

    return fecha


def _validar_hora(hora: str | None, campo: str, errores: dict[str, str]) -> str | None:
    if not hora:
        errores[campo] = "Ingresá una hora válida."
        return None

    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        errores[campo] = "Ingresá una hora en formato HH:MM."
        return hora

    return hora


def validar_paciente_form(form: MultiDict) -> tuple[dict[str, str | None], dict[str, str]]:
    datos: dict[str, str | None] = {
        "dni": _normalizar_texto(form.get("dni")),
        "nombres": _normalizar_texto(form.get("nombres")),
        "apellidos": _normalizar_texto(form.get("apellidos")),
        "telefono": _normalizar_opcional(form.get("telefono")),
        "email": _normalizar_opcional(form.get("email")),
        "fecha_nacimiento": _normalizar_opcional(form.get("fecha_nacimiento")),
        "direccion": _normalizar_opcional(form.get("direccion")),
    }
    errores: dict[str, str] = {}

    if not datos["dni"]:
        errores["dni"] = "Ingresá el DNI."
    elif len(str(datos["dni"])) > 15:
        errores["dni"] = "El DNI no puede superar 15 caracteres."

    if not datos["nombres"]:
        errores["nombres"] = "Ingresá los nombres."
    elif len(str(datos["nombres"])) > MAX_NOMBRE_LENGTH:
        errores["nombres"] = f"Los nombres no pueden superar {MAX_NOMBRE_LENGTH} caracteres."

    if not datos["apellidos"]:
        errores["apellidos"] = "Ingresá los apellidos."
    elif len(str(datos["apellidos"])) > MAX_NOMBRE_LENGTH:
        errores["apellidos"] = f"Los apellidos no pueden superar {MAX_NOMBRE_LENGTH} caracteres."

    if datos["telefono"] and len(str(datos["telefono"])) > MAX_TELEFONO_LENGTH:
        errores["telefono"] = f"El teléfono no puede superar {MAX_TELEFONO_LENGTH} caracteres."

    _validar_email(datos["email"], errores)
    datos["fecha_nacimiento"] = _validar_fecha(datos["fecha_nacimiento"], "fecha_nacimiento", errores)

    return datos, errores


def validar_especialidad_form(form: MultiDict) -> tuple[dict[str, str | None], dict[str, str]]:
    datos: dict[str, str | None] = {
        "nombre": _normalizar_texto(form.get("nombre")),
        "descripcion": _normalizar_opcional(form.get("descripcion")),
    }
    errores: dict[str, str] = {}

    if not datos["nombre"]:
        errores["nombre"] = "Ingresá el nombre de la especialidad."
    elif len(str(datos["nombre"])) > MAX_NOMBRE_LENGTH:
        errores["nombre"] = f"La especialidad no puede superar {MAX_NOMBRE_LENGTH} caracteres."

    return datos, errores


def validar_medico_form(form: MultiDict, requiere_password: bool = True) -> tuple[dict[str, str | int | None], dict[str, str]]:
    id_especialidad_raw = _normalizar_texto(form.get("id_especialidad"))
    estado = _normalizar_texto(form.get("estado")).upper() or "ACTIVO"
    datos: dict[str, str | int | None] = {
        "username": _normalizar_texto(form.get("username")),
        "password": form.get("password") or "",
        "nombres": _normalizar_texto(form.get("nombres")),
        "apellidos": _normalizar_texto(form.get("apellidos")),
        "email": _normalizar_opcional(form.get("email")),
        "telefono": _normalizar_opcional(form.get("telefono")),
        "estado": estado,
        "id_especialidad": None,
        "numero_colegiatura": _normalizar_texto(form.get("numero_colegiatura")),
    }
    errores: dict[str, str] = {}

    if not datos["username"]:
        errores["username"] = "Ingresá el usuario del médico."
    elif len(str(datos["username"])) > MAX_USERNAME_LENGTH:
        errores["username"] = f"El usuario no puede superar {MAX_USERNAME_LENGTH} caracteres."

    if requiere_password and not datos["password"]:
        errores["password"] = "Ingresá una contraseña inicial."
    elif datos["password"] and len(str(datos["password"])) > MAX_PASSWORD_LENGTH:
        errores["password"] = f"La contraseña no puede superar {MAX_PASSWORD_LENGTH} caracteres."

    if not datos["nombres"]:
        errores["nombres"] = "Ingresá los nombres."
    elif len(str(datos["nombres"])) > MAX_NOMBRE_LENGTH:
        errores["nombres"] = f"Los nombres no pueden superar {MAX_NOMBRE_LENGTH} caracteres."

    if not datos["apellidos"]:
        errores["apellidos"] = "Ingresá los apellidos."
    elif len(str(datos["apellidos"])) > MAX_NOMBRE_LENGTH:
        errores["apellidos"] = f"Los apellidos no pueden superar {MAX_NOMBRE_LENGTH} caracteres."

    _validar_email(datos["email"], errores)

    if datos["telefono"] and len(str(datos["telefono"])) > MAX_TELEFONO_LENGTH:
        errores["telefono"] = f"El teléfono no puede superar {MAX_TELEFONO_LENGTH} caracteres."

    if estado not in ESTADOS_USUARIO:
        errores["estado"] = "Seleccioná un estado válido."

    if not id_especialidad_raw:
        errores["id_especialidad"] = "Seleccioná una especialidad."
    else:
        try:
            datos["id_especialidad"] = int(id_especialidad_raw)
        except ValueError:
            errores["id_especialidad"] = "Seleccioná una especialidad válida."

    if not datos["numero_colegiatura"]:
        errores["numero_colegiatura"] = "Ingresá el número de colegiatura."
    elif len(str(datos["numero_colegiatura"])) > 30:
        errores["numero_colegiatura"] = "La colegiatura no puede superar 30 caracteres."

    return datos, errores


def validar_horario_form(form: MultiDict, id_medico: int | None = None) -> tuple[dict[str, str | int | None], dict[str, str]]:
    estado = _normalizar_texto(form.get("estado")).upper() or "DISPONIBLE"
    datos: dict[str, str | int | None] = {
        "id_medico": id_medico,
        "fecha": _normalizar_opcional(form.get("fecha")),
        "hora_inicio": _normalizar_opcional(form.get("hora_inicio")),
        "hora_fin": _normalizar_opcional(form.get("hora_fin")),
        "estado": estado,
    }
    errores: dict[str, str] = {}

    if id_medico is None:
        id_medico_raw = _normalizar_texto(form.get("id_medico"))
        try:
            datos["id_medico"] = int(id_medico_raw)
        except ValueError:
            errores["id_medico"] = "Seleccioná un médico válido."

    if not datos["fecha"]:
        errores["fecha"] = "Ingresá la fecha del horario."
    else:
        datos["fecha"] = _validar_fecha(datos["fecha"], "fecha", errores)

    datos["hora_inicio"] = _validar_hora(datos["hora_inicio"], "hora_inicio", errores)
    datos["hora_fin"] = _validar_hora(datos["hora_fin"], "hora_fin", errores)

    if datos["hora_inicio"] and datos["hora_fin"] and str(datos["hora_inicio"]) >= str(datos["hora_fin"]):
        errores["hora_fin"] = "La hora de fin debe ser posterior a la hora de inicio."

    if estado not in ESTADOS_HORARIO:
        errores["estado"] = "Seleccioná un estado válido."

    return datos, errores



def _validar_entero_positivo(valor: str | None, campo: str, errores: dict[str, str], mensaje: str) -> int | None:
    texto = _normalizar_texto(valor)
    if not texto:
        errores[campo] = mensaje
        return None

    try:
        numero = int(texto)
    except ValueError:
        errores[campo] = mensaje
        return None

    if numero <= 0:
        errores[campo] = mensaje
        return None

    return numero


def validar_programacion_cita_form(form: MultiDict) -> tuple[dict[str, str | int | None], dict[str, str]]:
    datos: dict[str, str | int | None] = {
        "id_paciente": None,
        "id_medico": None,
        "fecha": _normalizar_opcional(form.get("fecha")),
        "hora": _normalizar_opcional(form.get("hora")),
        "motivo_consulta": _normalizar_opcional(form.get("motivo_consulta")),
    }
    errores: dict[str, str] = {}

    datos["id_paciente"] = _validar_entero_positivo(
        form.get("id_paciente"),
        "id_paciente",
        errores,
        "Seleccioná un paciente válido.",
    )
    datos["id_medico"] = _validar_entero_positivo(
        form.get("id_medico"),
        "id_medico",
        errores,
        "Seleccioná un médico válido.",
    )

    if not datos["fecha"]:
        errores["fecha"] = "Ingresá la fecha de la cita."
    else:
        datos["fecha"] = _validar_fecha(str(datos["fecha"]), "fecha", errores)

    datos["hora"] = _validar_hora(str(datos["hora"] or ""), "hora", errores)

    if datos["motivo_consulta"] and len(str(datos["motivo_consulta"])) > 255:
        errores["motivo_consulta"] = "El motivo no puede superar 255 caracteres."

    return datos, errores


def validar_reprogramacion_cita_form(form: MultiDict) -> tuple[dict[str, str | int | None], dict[str, str]]:
    datos: dict[str, str | int | None] = {
        "id_medico": None,
        "fecha": _normalizar_opcional(form.get("fecha")),
        "hora": _normalizar_opcional(form.get("hora")),
        "motivo_consulta": _normalizar_opcional(form.get("motivo_consulta")),
    }
    errores: dict[str, str] = {}

    datos["id_medico"] = _validar_entero_positivo(
        form.get("id_medico"),
        "id_medico",
        errores,
        "Seleccioná un médico válido.",
    )

    if not datos["fecha"]:
        errores["fecha"] = "Ingresá la nueva fecha de la cita."
    else:
        datos["fecha"] = _validar_fecha(str(datos["fecha"]), "fecha", errores)

    datos["hora"] = _validar_hora(str(datos["hora"] or ""), "hora", errores)

    if datos["motivo_consulta"] and len(str(datos["motivo_consulta"])) > 255:
        errores["motivo_consulta"] = "El motivo no puede superar 255 caracteres."

    return datos, errores


def validar_cancelacion_cita_form(form: MultiDict) -> tuple[dict[str, str], dict[str, str]]:
    datos = {"motivo_cancelacion": _normalizar_texto(form.get("motivo_cancelacion") or form.get("motivo"))}
    errores: dict[str, str] = {}

    if not datos["motivo_cancelacion"]:
        errores["motivo_cancelacion"] = "Ingresá el motivo de cancelación."
    elif len(datos["motivo_cancelacion"]) > 255:
        errores["motivo_cancelacion"] = "El motivo de cancelación no puede superar 255 caracteres."

    return datos, errores


def validar_historial_form(form: MultiDict) -> tuple[dict[str, str | None], dict[str, str]]:
    datos = {
        "observacion": _normalizar_texto(form.get("observacion") or form.get("observaciones")),
    }
    errores: dict[str, str] = {}

    if not datos["observacion"]:
        errores["observacion"] = "Ingresá la observación clínica de la atención."
    elif len(datos["observacion"]) > 5000:
        errores["observacion"] = "La observación clínica es demasiado extensa."

    return datos, errores
