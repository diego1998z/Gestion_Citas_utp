# Sistema de Gestión de Citas Médicas

Sistema web MVC para la Clínica Universitaria de Comas. Permite registrar pacientes, administrar médicos y especialidades, configurar horarios, programar/cancelar/reprogramar citas, registrar atenciones en historial y consultar un reporte básico de citas.

## Stack tecnológico

- Backend: Python + Flask.
- Frontend: HTML, CSS y JavaScript server-rendered.
- Base de datos: MySQL con motor InnoDB.
- Arquitectura: MVC con Blueprints de Flask.
- Seguridad: sesión Flask, roles, hashing de contraseñas con Werkzeug y consultas SQL parametrizadas.

## Estructura MVC

```text
app/
  models/        # SQL parametrizado y transacciones
  controllers/   # rutas, validación, reglas de negocio y RBAC
  views/         # templates HTML sin conexión directa a BD
  static/        # CSS, JS e imágenes
config/          # configuración Flask/MySQL
database/        # schema.sql y seed.sql
docs/            # documentación técnica de entrega
run.py           # punto de entrada de Flask
```

Regla central: las vistas no ejecutan SQL ni abren conexiones. Toda consulta pasa por controlador y modelo.

## Instalación local

1. Crear entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Copiar configuración de ejemplo:

```powershell
Copy-Item .env.example .env
```

4. Editar `.env` con tus credenciales MySQL:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=cambiar-esta-clave-en-produccion
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=gestion_citas_medicas
LOG_LEVEL=INFO
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_USE_TLS=true
SMTP_FROM=
```

## Creación de base de datos

Ejecutar los scripts SQL en este orden:

```powershell
mysql -u root -p < database/schema.sql
mysql -u root -p gestion_citas_medicas < database/seed.sql
```

`schema.sql` crea la base `gestion_citas_medicas`, tablas InnoDB, claves primarias/foráneas, ENUMs e índices. `seed.sql` carga datos mínimos de demostración.

## Usuarios demo

Si cargás `database/seed.sql`:

| Usuario | Contraseña | Rol | Registro relacionado |
| --- | --- | --- | --- |
| `admin` | `Admin123*` | `ADMINISTRADOR` | `administrador` |
| `medico` | `Medico123*` | `MEDICO` | `medico` con especialidad `Medicina General` |
| `recepcionista` | `Recepcion123*` | `RECEPCIONISTA` | `recepcionista` |

## Ejecución local

```powershell
flask run
```

No hay paso de build: el proyecto usa Flask con templates renderizados en servidor.

## Despliegue en Railway

Configurar estas variables en Railway antes de desplegar:

- `SECRET_KEY`: obligatoria en producción.
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`: conexión a la base MySQL ya creada por Railway.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_FROM`: opcionales; si no se configuran, el sistema no enviará correos SMTP.

Railway ejecuta el `Procfile`:

```text
web: python scripts/apply_database.py && gunicorn run:app --bind 0.0.0.0:$PORT
```

Antes de iniciar Gunicorn, `scripts/apply_database.py` aplica `database/schema.sql`, `database/migrations/20260625_appointment_workflow.sql` y `database/seed.sql` sobre la base configurada. El script omite `CREATE DATABASE` y `USE ...` porque en Railway la base ya existe y el usuario de la app puede no tener permisos para crear bases.

## Roles

- `ADMINISTRADOR`: acceso a pacientes, médicos, especialidades, horarios, citas, historial y reportes.
- `RECEPCIONISTA`: gestión operativa de pacientes y citas.
- `MEDICO`: consulta de citas, atención y registro de historial.

## Reglas de negocio principales

- Validar disponibilidad del médico antes de programar una cita.
- No permitir dos citas activas (`PENDIENTE` o `CONFIRMADA`) para el mismo médico, fecha y hora.
- Cancelar una cita registra motivo y fecha de cancelación.
- Notificar al paciente envía correo SMTP; solo si el envío es exitoso actualiza `notificado` y `fecha_notificacion`. Si SMTP no está configurado o falla, registra evento de fallo y no marca la cita como notificada.
- Reprogramar crea una nueva cita, marca la original como `REPROGRAMADA` y registra auditoría en `cita_evento`.
- El médico puede crear citas de seguimiento para el mismo paciente y el mismo médico desde sus citas activas o atendidas.
- Los recordatorios automáticos quedan disponibles como función de servicio (`send_pending_reminders`) y evitan duplicados usando `cita.notificado`.
- El historial se genera desde una cita existente; `historial_cita` no duplica `id_paciente`.

## Documentación complementaria

- `docs/diccionario_datos.md`: tablas, campos y reglas principales.
- `docs/mapa_endpoints.md`: rutas, método, rol y controlador.
- `docs/checklist_validacion.md`: guía de validación manual y checklist técnico mínimo.
