# Documentación técnica entregable

Este documento corresponde al inventario real de la documentación técnica entregada para el Sistema de Gestión de Citas Médicas de la Clínica Universitaria de Comas. Su finalidad es dejar evidencia de qué documentos acompañan al proyecto, qué archivo los contiene, qué información cubren y cuál es su estado al momento de la entrega.

## 1. Objetivo

El objetivo de esta documentación técnica entregable es facilitar la revisión, instalación, mantenimiento y validación del sistema por parte de un evaluador, docente o futuro desarrollador.

La documentación entregada permite verificar:

- Cómo se instala y ejecuta el sistema.
- Cómo está organizada la arquitectura MVC.
- Cómo está diseñada la base de datos MySQL.
- Qué rutas y módulos existen en la aplicación.
- Qué reglas de seguridad, validación y manejo de errores se aplican.
- Qué pruebas y criterios de validación fueron considerados.
- Qué convenciones de codificación, seguridad y Git se usaron en el proyecto.

## 2. Inventario real de documentación entregada

| Entregable | Archivo entregado | Descripción real | Estado |
|---|---|---|---|
| README de instalación | `README.md` | Documento principal del proyecto. Presenta el sistema, objetivo, stack tecnológico, estructura general, requisitos, variables de entorno, configuración de base de datos, ejecución local, usuarios demo, roles y reglas principales del flujo de citas. | Entregado y actualizado |
| Diccionario de datos | `docs/diccionario_datos.md` | Documenta la estructura de la base de datos `gestion_citas_medicas`, incluyendo tablas, campos, tipos de datos, claves primarias, claves foráneas, restricciones, estados `ENUM` y relaciones principales. Incluye la tabla `cita_evento` para trazabilidad de cambios en las citas. | Entregado y actualizado |
| Mapa de endpoints | `docs/mapa_endpoints.md` | Lista las rutas reales del sistema, método HTTP, roles autorizados, controlador asociado y descripción funcional. Incluye rutas de autenticación, pacientes, médicos, horarios, citas, historial clínico, reportes básicos y endpoints auxiliares. | Entregado y actualizado |
| Manual técnico | `docs/manual_tecnico.md` | Explica la arquitectura MVC, estructura del proyecto, configuración, conexión a MySQL, seguridad, manejo de errores, logs, transacciones, despliegue en Railway, reglas de negocio y mantenimiento técnico del sistema. | Entregado y actualizado |
| Manual de usuario | `docs/manual_usuario.md` | Explica el uso funcional del sistema por rol: administrador, recepcionista y médico. Describe el inicio de sesión, gestión de pacientes, programación de citas, confirmación, cancelación, reprogramación, atención médica e historial. | Entregado |
| Checklist de validación | `docs/checklist_validacion.md` | Contiene la lista de verificación usada para validar el sistema antes de la entrega. Cubre instalación, seguridad, MVC, pacientes, médicos, horarios, citas, historial clínico, reportes básicos, trazabilidad con `cita_evento` y manejo de errores. | Entregado y actualizado |
| Convenciones, seguridad y Git | `docs/convenciones_seguridad_git.md` | Resume los estándares de codificación, convenciones de nombres, seguridad aplicada, control de roles, consultas parametrizadas, CSRF, logs, rollback, commits semánticos y recomendaciones de flujo Git. | Entregado y actualizado |

## 3. Documentos entregados

Los archivos entregados como documentación técnica del proyecto son:

- `README.md`
- `docs/diccionario_datos.md`
- `docs/mapa_endpoints.md`
- `docs/manual_tecnico.md`
- `docs/manual_usuario.md`
- `docs/checklist_validacion.md`
- `docs/convenciones_seguridad_git.md`

La tabla `cita_evento`, agregada para registrar la trazabilidad de confirmaciones, cancelaciones, reprogramaciones, notificaciones y atenciones, se encuentra documentada en los archivos correspondientes, principalmente en el diccionario de datos, manual técnico y checklist de validación.

## 4. Relación entre documentación y módulos del sistema

| Módulo o aspecto del sistema | Documento donde se evidencia |
|---|---|
| Instalación y ejecución local | `README.md` |
| Configuración de variables de entorno | `README.md`, `docs/manual_tecnico.md` |
| Arquitectura MVC | `docs/manual_tecnico.md` |
| Base de datos y relaciones | `docs/diccionario_datos.md`, `docs/manual_tecnico.md` |
| Tabla `cita_evento` y trazabilidad | `docs/diccionario_datos.md`, `docs/manual_tecnico.md`, `docs/checklist_validacion.md` |
| Rutas y roles permitidos | `docs/mapa_endpoints.md` |
| Uso del sistema por rol | `docs/manual_usuario.md` |
| Seguridad y validaciones | `docs/convenciones_seguridad_git.md`, `docs/manual_tecnico.md` |
| Manejo de errores, logs y rollback | `docs/convenciones_seguridad_git.md`, `docs/manual_tecnico.md` |
| Pruebas manuales y criterios de revisión | `docs/checklist_validacion.md` |

## 5. Criterios de aceptación cumplidos

La documentación técnica entregada cumple con los siguientes criterios de aceptación:

- El `README.md` permite identificar el sistema, conocer su stack tecnológico, configurar el entorno y ejecutar la aplicación.
- El diccionario de datos documenta las tablas principales de la base de datos, incluyendo `cita_evento`.
- El mapa de endpoints identifica las rutas del sistema, los métodos HTTP, los roles autorizados y los controladores responsables.
- El manual técnico explica la arquitectura MVC, la estructura del proyecto, la configuración, la seguridad, las transacciones y el despliegue.
- El manual de usuario describe las acciones principales que puede realizar cada rol del sistema.
- El checklist de validación cubre los flujos principales y casos críticos del sistema.
- La documentación de convenciones, seguridad y Git resume los estándares aplicados en el desarrollo.
- No se incluyen contraseñas reales, tokens SMTP ni variables sensibles de producción.
- No se utiliza la expresión "archivo sugerido"; todos los archivos listados corresponden a documentos existentes en el proyecto.

## 6. Estado final del punto 7

El punto 7 queda desarrollado como inventario real de documentación técnica entregada. Los documentos listados existen dentro del repositorio y describen el estado actual del sistema, incluyendo instalación, arquitectura, base de datos, endpoints, uso por roles, seguridad, validaciones, checklist de pruebas y convenciones de desarrollo.
