# Sistema de Gestión de Citas Médicas

Sistema web MVC para la Clínica Universitaria de Comas. Permite registrar pacientes, administrar médicos y especialidades, configurar horarios, programar/cancelar/reprogramar citas, registrar atenciones en historial y consultar un reporte básico de citas.

## Stack tecnológico

- Backend: Python + Flask.
- Frontend: HTML, CSS y JavaScript server-rendered.
- Base de datos: MySQL con motor InnoDB.
- Arquitectura: MVC con Blueprints de Flask.
- Seguridad: sesión Flask, roles, hashing de contraseñas con Werkzeug, consultas SQL parametrizadas, protección CSRF en formularios POST y `SECRET_KEY` obligatoria en producción.

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
Copy-Item .env.example config/.env
```

4. Editar `config/.env` con tus credenciales MySQL y SMTP:

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
WTF_CSRF_TIME_LIMIT=3600

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=tu-correo@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM=tu-correo@gmail.com
```

## Creación de base de datos

Ejecutar los scripts SQL en este orden:

```powershell
mysql -u root -p < database/schema.sql
mysql -u root -p gestion_citas_medicas < database/seed.sql
```

`schema.sql` crea la base `gestion_citas_medicas`, tablas InnoDB, claves primarias/foráneas, ENUMs e índices. `seed.sql` carga datos mínimos de demostración.

## Usuarios demo

Si cargás `database/seed.sql`, se crean usuarios demo ligados a nombres reales de prueba. El script almacena únicamente `password_hash`; por seguridad no se documentan contraseñas reales ni secretos de producción.

| Usuario | Rol | Registro relacionado |
| --- | --- | --- |
| `patricia.salas` | `ADMINISTRADOR` | Administrador Patricia Elena Salas Medina |
| `roberto.rivas` | `ADMINISTRADOR` | Administrador Roberto Carlos Rivas Alarcon |
| `valeria.nunez` | `RECEPCIONISTA` | Recepcionista Valeria Milagros Nuñez Castro |
| `marisol.castro` | `RECEPCIONISTA` | Recepcionista Marisol Andrea Castro Benavides |
| `luis.quispe` | `MEDICO` | Médico Luis Alberto Quispe Mamani |
| `ana.huaman` | `MEDICO` | Médico Ana Lucia Huaman Flores |
| `carlos.choque` | `MEDICO` | Médico Carlos Enrique Choque Rojas |
| `rosa.condori` | `MEDICO` | Médico Rosa Maria Condori Salazar |
| `miguel.torres` | `MEDICO` | Médico Miguel Angel Torres Paredes |
| `elena.villanueva` | `MEDICO` | Médico Elena Pilar Villanueva Soto |

## Ejecución local

```powershell
flask run
```

No hay paso de build: el proyecto usa Flask con templates renderizados en servidor.

## Seguridad operativa

- En desarrollo, si no definís `SECRET_KEY`, Flask usa una clave temporal para facilitar pruebas locales.
- En producción (`APP_ENV=production` o `FLASK_ENV=production`), `SECRET_KEY` es obligatoria y la app falla al arrancar si falta.
- Todos los formularios POST incluyen token CSRF. Si el formulario expira, recargá la página y reenviá la operación.
- Las cookies de sesión son `HttpOnly`, `SameSite=Lax` y `Secure` cuando el entorno es production.

## Roles

- `ADMINISTRADOR`: acceso a pacientes, médicos, especialidades, horarios, citas, historial y reportes.
- `RECEPCIONISTA`: gestión operativa de pacientes y citas.
- `MEDICO`: consulta de citas, atención y registro de historial.

## Reglas de negocio principales

- Validar disponibilidad del médico antes de programar una cita.
- No permitir dos citas activas (`PENDIENTE` o `CONFIRMADA`) para el mismo médico, fecha y hora.
- Confirmar únicamente citas en estado `PENDIENTE`.
- Cancelar una cita registra motivo y fecha de cancelación.
- Notificar al paciente envía correo por SMTP y, si el envío fue exitoso, actualiza `notificado` y `fecha_notificacion`. Para Gmail, configurá `SMTP_USER`, `SMTP_PASSWORD` con una App Password y `SMTP_FROM` en `config/.env`.
- Reprogramar crea una nueva cita y marca la original como `REPROGRAMADA`.
- El historial se genera desde una cita existente; `historial_cita` no duplica `id_paciente`.

## Documentación complementaria

- `docs/diccionario_datos.md`: tablas, campos y reglas principales.
- `docs/mapa_endpoints.md`: rutas, método, rol y controlador.
- `docs/checklist_validacion.md`: guía de validación manual y checklist técnico mínimo.
- `docs/documentacion_tecnica_entregable.md`: desarrollo del punto 7 de la guía e inventario de entregables.
- `docs/manual_tecnico.md`: arquitectura, configuración, seguridad, logs, Git y mantenimiento.
- `docs/manual_usuario.md`: guía operativa por rol.
- `docs/convenciones_seguridad_git.md`: evidencia de Clean Code, seguridad, manejo de errores y flujo Git.
