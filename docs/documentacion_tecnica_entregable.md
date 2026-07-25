# Documentación técnica entregable

Este documento desarrolla el punto 7 de la guía de codificación del sistema. Su objetivo es inventariar los documentos, archivos y evidencias entregados para considerar aceptado el sistema o cada módulo funcional.

## 1. Objetivo del entregable

La documentación técnica entregable permite que el sistema pueda ser instalado, revisado, mantenido y evaluado por otra persona sin depender únicamente del equipo desarrollador.

Para el Sistema de Gestión de Citas Médicas, la documentación debe demostrar:

- Cómo está construido el sistema.
- Cómo se instala y ejecuta.
- Cómo está diseñada la base de datos.
- Qué rutas o endpoints existen.
- Qué roles pueden usar cada funcionalidad.
- Qué reglas de negocio se aplican.
- Qué validaciones se realizaron antes de la entrega.

## 2. Inventario de documentos entregados

| Entregable | Archivo entregado | Estado actual | Propósito |
|---|---|---|---|
| README de instalación | `README.md` | Entregado | Explicar requisitos, configuración, base de datos, usuarios demo y ejecución local. |
| Diccionario de datos | `docs/diccionario_datos.md` | Entregado | Documentar tablas, campos, tipos de datos, claves primarias, claves foráneas y reglas. |
| Mapa de endpoints | `docs/mapa_endpoints.md` | Entregado | Listar rutas, métodos HTTP, roles autorizados y controladores. |
| Checklist de validación | `docs/checklist_validacion.md` | Entregado | Guiar pruebas manuales y revisión técnica mínima antes de entregar. |
| Manual técnico | `docs/manual_tecnico.md` | Entregado | Explicar arquitectura, flujo interno, configuración, seguridad, logs y mantenimiento. |
| Manual de usuario | `docs/manual_usuario.md` | Entregado | Explicar el uso del sistema por rol con pasos claros. |
| Convenciones, seguridad y Git | `docs/convenciones_seguridad_git.md` | Entregado | Resumir estándares de codificación, seguridad, manejo de errores y flujo Git. |

## 3. README de instalación

El README debe ser el primer documento que revise una persona externa al proyecto.

Debe incluir:

1. Nombre del sistema.
2. Objetivo general.
3. Stack tecnológico.
4. Estructura de carpetas.
5. Requisitos previos.
6. Instalación de dependencias.
7. Configuración del archivo `.env`.
8. Creación de la base de datos.
9. Ejecución de scripts SQL.
10. Usuarios de prueba.
11. Comando para iniciar la aplicación.
12. Reglas de negocio principales.

Archivo relacionado: `README.md`.

## 4. Diccionario de datos

El diccionario de datos debe documentar la estructura de la base de datos `gestion_citas_medicas`.

Debe incluir por cada tabla:

- Nombre de la tabla.
- Descripción funcional.
- Campos.
- Tipo de dato.
- Si el campo permite `NULL`.
- Clave primaria.
- Claves foráneas.
- Restricciones `UNIQUE`.
- Campos de auditoría.
- Estados permitidos cuando se use `ENUM`.

Tablas mínimas documentadas:

- `usuario_sistema`
- `administrador`
- `recepcionista`
- `medico`
- `especialidad`
- `horario`
- `paciente`
- `cita`
- `historial_cita`
- `cita_evento`

Archivo relacionado: `docs/diccionario_datos.md`.

## 5. Mapa de endpoints

El mapa de endpoints debe permitir revisar rápidamente qué rutas existen y qué función cumple cada una.

Debe incluir:

- Método HTTP.
- Ruta.
- Rol requerido.
- Controlador responsable.
- Descripción de la acción.
- Si la ruta renderiza una vista o devuelve JSON.

Ejemplo de formato:

| Método | Ruta | Rol requerido | Controlador | Descripción |
|---|---|---|---|---|
| GET / POST | `/login` | Público | `auth_controller.login` | Inicio de sesión. |
| GET | `/pacientes` | `ADMINISTRADOR`, `RECEPCIONISTA` | `paciente_controller.index` | Lista pacientes. |
| POST | `/citas/<id_cita>/confirmar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.confirmar` | Confirma una cita pendiente. |
| POST | `/citas/<id_cita>/cancelar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.cancelar` | Cancela una cita con motivo. |

Archivo relacionado: `docs/mapa_endpoints.md`.

## 6. Manual técnico

El manual técnico está orientado al profesor, evaluador o futuro desarrollador que deba entender cómo funciona internamente el sistema.

Debe incluir:

### 6.1 Arquitectura

- Patrón MVC utilizado.
- Responsabilidad de modelos, controladores y vistas.
- Uso de Blueprints de Flask.
- Regla principal: las vistas no acceden directamente a la base de datos.

### 6.2 Estructura del proyecto

Debe explicar la función de las carpetas principales:

```text
app/
  models/
  controllers/
  views/
  static/
  utils/
config/
database/
docs/
logs/
run.py
```

### 6.3 Configuración

Debe explicar:

- Variables de entorno usadas.
- Conexión a MySQL.
- Archivo `.env`.
- Archivo `.env.example`.
- Configuración de logs.

### 6.4 Persistencia

Debe explicar:

- Uso de MySQL.
- Motor InnoDB.
- Uso de claves foráneas.
- Uso de transacciones.
- Consultas parametrizadas.
- Scripts `database/schema.sql` y `database/seed.sql`.

### 6.5 Seguridad

Debe documentar:

- Autenticación por sesión.
- Hashing de contraseñas con Werkzeug.
- Control de acceso por roles.
- Validación de formularios.
- Prevención de inyección SQL mediante parámetros.
- Prevención básica de XSS mediante escape automático de Jinja.
- Manejo de redirecciones internas seguras.

### 6.6 Manejo de errores y logs

Debe explicar:

- Uso de `try-except` en operaciones críticas.
- Mensajes amigables para el usuario.
- Registro técnico en `logs/app.log`.
- Manejadores globales para errores `403`, `404` y `500`.

### 6.7 Reglas de negocio

Debe incluir las principales reglas del sistema:

- Validar disponibilidad antes de programar una cita.
- No permitir dos citas activas para el mismo médico, fecha y hora.
- Confirmar únicamente citas en estado `PENDIENTE`.
- Registrar motivo y fecha al cancelar una cita.
- Registrar notificación del paciente.
- Reprogramar creando una nueva cita y marcando la original como `REPROGRAMADA`.
- Crear historial solamente desde una cita existente.

Archivo relacionado: `docs/manual_tecnico.md`.

## 7. Manual de usuario

El manual de usuario debe estar escrito para una persona que utilizará el sistema, no para un desarrollador.

Debe organizarse por rol:

### 7.1 Administrador

Debe explicar cómo:

- Iniciar sesión.
- Gestionar pacientes.
- Gestionar médicos.
- Gestionar especialidades.
- Registrar horarios.
- Revisar citas.
- Consultar historial.
- Revisar reportes.

### 7.2 Recepcionista

Debe explicar cómo:

- Registrar pacientes.
- Programar citas.
- Confirmar citas pendientes.
- Cancelar citas.
- Reprogramar citas.
- Notificar al paciente.
- Consultar historial.

### 7.3 Médico

Debe explicar cómo:

- Consultar sus citas.
- Marcar una cita como atendida.
- Registrar observaciones clínicas.
- Marcar una cita como no asistida.
- Consultar historial de atención.

### 7.4 Capturas recomendadas

El manual de usuario debería incluir capturas de:

- Login.
- Panel principal.
- Listado de pacientes.
- Formulario de paciente.
- Listado de médicos.
- Gestión de horarios.
- Programación de cita.
- Reprogramación de cita.
- Historial de cita.
- Reporte de citas.

Archivo relacionado: `docs/manual_usuario.md`.

## 8. Checklist de validación

Antes de entregar el proyecto, se debe ejecutar una revisión manual usando el checklist.

Debe validar:

- Instalación.
- Base de datos.
- Seguridad.
- Separación MVC.
- Flujo de pacientes.
- Flujo de médicos.
- Flujo de horarios.
- Flujo de citas.
- Flujo de historial.
- Reporte básico de citas.
- Trazabilidad de eventos de cita.
- Manejo de errores.

Archivo relacionado: `docs/checklist_validacion.md`.

## 9. Criterios de aceptación de la documentación

La documentación técnica se considera aceptada cuando:

- El README permite instalar y ejecutar el sistema desde cero.
- El diccionario de datos coincide con `database/schema.sql`.
- El mapa de endpoints coincide con las rutas reales de `app/controllers/`.
- El manual técnico explica la arquitectura y decisiones principales.
- El manual de usuario permite operar el sistema sin leer el código.
- El checklist de validación cubre los flujos principales.
- No se documentan contraseñas reales ni datos sensibles de producción.
- No se exponen errores internos de base de datos al usuario final.

## 10. Estado actual del punto 7

El punto 7 se encuentra desarrollado como inventario real de documentación técnica entregada.

Existen:

- `README.md`
- `docs/diccionario_datos.md`
- `docs/mapa_endpoints.md`
- `docs/checklist_validacion.md`
- `docs/manual_tecnico.md`
- `docs/manual_usuario.md`
- `docs/convenciones_seguridad_git.md`

Queda pendiente para una entrega visual más completa:

- Agregar capturas de pantalla al manual de usuario cuando la UI final quede congelada.
- Mantener la documentación sincronizada cuando se agreguen nuevas rutas, tablas o reglas de negocio.
