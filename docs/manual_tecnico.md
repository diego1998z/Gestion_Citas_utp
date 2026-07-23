# Manual técnico

## 1. Propósito

Sistema web MVC para gestionar citas médicas de la Clínica Universitaria de Comas. Cubre pacientes, médicos, especialidades, horarios, citas, confirmación, reprogramación, cancelación, notificación, historial clínico básico y reportes administrativos.

## 2. Stack y arquitectura

- Backend: Python con Flask.
- Frontend: HTML, CSS y JavaScript renderizados desde templates Jinja.
- Base de datos: MySQL con motor InnoDB.
- Arquitectura: MVC usando Blueprints de Flask.
- Persistencia: modelos con SQL parametrizado y transacciones.

Responsabilidades por capa:

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Modelo | `app/models/` | Consultas SQL, acceso a datos y transacciones. |
| Controlador | `app/controllers/` | Rutas, validación, reglas de negocio, sesión y autorización. |
| Vista | `app/views/` | Presentación HTML/Jinja. No debe conectarse a MySQL ni ejecutar SQL. |
| Utilidades | `app/utils/` | Autenticación, validadores, decoradores y helpers compartidos. |

## 3. Configuración

Variables principales:

| Variable | Uso | Requerida en producción |
|---|---|---|
| `FLASK_APP` | Punto de entrada Flask (`run.py`). | Sí |
| `FLASK_ENV` / `APP_ENV` | Entorno de ejecución. `production` activa reglas más estrictas. | Sí |
| `SECRET_KEY` | Firma de sesión y tokens CSRF. | Sí |
| `MYSQL_HOST` | Host de MySQL. | Sí |
| `MYSQL_PORT` | Puerto de MySQL. | Sí |
| `MYSQL_USER` | Usuario de MySQL. | Sí |
| `MYSQL_PASSWORD` | Contraseña de MySQL. | Sí |
| `MYSQL_DATABASE` | Base `gestion_citas_medicas`. | Sí |
| `LOG_LEVEL` | Nivel de logging. | No |
| `WTF_CSRF_TIME_LIMIT` | Vigencia del token CSRF en segundos. | No |
| `SMTP_HOST` | Servidor SMTP. Por defecto `smtp.gmail.com`. | Sí, si se usan notificaciones |
| `SMTP_PORT` | Puerto SMTP entero. Por defecto `587`. | Sí, si se usan notificaciones |
| `SMTP_USE_TLS` | Activa STARTTLS (`true/false`, `1/0`, `yes/no`, `on/off`). Por defecto `true`. | Sí, si se usan notificaciones |
| `SMTP_USER` | Usuario/correo autenticado del remitente. | Sí, si el SMTP autentica |
| `SMTP_PASSWORD` | Password SMTP. En Gmail debe ser una App Password, no la contraseña normal. | Sí, si el SMTP autentica |
| `SMTP_FROM` | Remitente visible. Si no se define, usa `SMTP_USER`. | Sí, si se usan notificaciones |

Regla de seguridad: si `APP_ENV=production` o `FLASK_ENV=production`, la aplicación no debe arrancar sin `SECRET_KEY` explícita. En desarrollo se mantiene una clave temporal para facilitar ejecución local. La configuración se puede cargar desde `.env` y desde `config/.env`; `config/.env` tiene precedencia para permitir ajustes locales del proyecto sin tocar secretos reales.

Para notificaciones por correo, el servicio usa SMTP. Con Gmail, crear una App Password en la cuenta de Google y colocarla en `SMTP_PASSWORD`; no usar ni versionar la contraseña normal de la cuenta.

## 4. Base de datos

- Script de estructura: `database/schema.sql`.
- Script de datos demo: `database/seed.sql`.
- Base: `gestion_citas_medicas`.
- Tablas principales: `usuario_sistema`, `administrador`, `recepcionista`, `medico`, `especialidad`, `horario`, `paciente`, `cita`, `historial_cita`.
- Convenciones: tablas en singular, campos en `snake_case`, PK `id_tabla`, FK `id_tabla_relacionada`.
- Motor: InnoDB para soportar claves foráneas.

## 5. Seguridad implementada

- Autenticación por sesión Flask.
- Hashing de contraseñas con Werkzeug.
- Autorización por roles (`ADMINISTRADOR`, `RECEPCIONISTA`, `MEDICO`).
- En login, el rol enviado por el formulario se normaliza, se valida contra roles permitidos y debe coincidir con el rol real del usuario autenticado antes de crear la sesión.
- Consultas SQL parametrizadas para prevenir inyección SQL.
- Validación server-side de formularios antes de llamar al modelo.
- Escape automático de Jinja para reducir riesgo de XSS en vistas.
- Protección CSRF en formularios POST mediante Flask-WTF (`CSRFProtect`).
- Cookies de sesión `HttpOnly`, `SameSite=Lax` y `Secure` en producción.
- Manejo seguro de `SECRET_KEY`: obligatoria en producción, fallback solo para desarrollo.

Brechas o mejoras recomendadas:

- Forzar HTTPS desde proxy/servidor web en producción.
- Configurar rotación externa de secretos y no subir `.env` al repositorio.
- Agregar rate limiting para `/login` si se publica en internet.
- Revisar cabeceras de seguridad HTTP (`Content-Security-Policy`, `X-Frame-Options`) si se despliega en producción.

## 6. Manejo de errores y logs

- Logs en `logs/app.log` con `RotatingFileHandler`.
- Rotación: 1 MB por archivo, hasta 5 respaldos.
- Errores `403`, `404` y `500` renderizan vistas amigables.
- Errores CSRF se registran como advertencia y responden con la vista `403`.
- Operaciones críticas de base de datos usan transacciones con `commit`/`rollback`.

Regla: el usuario final ve mensajes amigables; el detalle técnico queda en logs.

## 7. Flujo de desarrollo y Git

- Usar ramas descriptivas: `feature/...`, `bugfix/...`, `develop`, `main` o `master` según el repositorio.
- Commits convencionales:
  - `feat: agregar módulo de programación de citas`
  - `fix: corregir validación de horario`
  - `docs: actualizar documentación técnica`
  - `refactor: mejorar estructura de modelo cita`
- No incluir `Co-Authored-By` ni atribución automática en commits.
- No versionar `.env`, logs ni artefactos temporales.

## 8. Convenciones y Clean Code

- Clases en PascalCase: `CitaModel`, `PacienteController`.
- Funciones, variables y archivos Python en `snake_case`.
- Constantes en `UPPER_SNAKE_CASE`.
- Nombres descriptivos, sin variables genéricas como `x`, `data1` o `temp`.
- Funciones cortas y con una responsabilidad clara.
- Reglas de negocio en controladores/utilidades, no en templates.
- SQL solamente en modelos.

## 9. Validación previa a entrega

Sin ejecutar build, se recomienda:

```powershell
python -m py_compile app/__init__.py config/settings.py app/controllers/*.py app/models/*.py app/utils/*.py
git diff --check
```

También revisar que `app/views/` no contenga SQL ni conexiones directas a base de datos.
