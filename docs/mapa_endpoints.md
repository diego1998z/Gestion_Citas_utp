# Mapa de endpoints

Las rutas protegidas usan sesión Flask. Los roles se validan en controladores con decoradores; las vistas no contienen SQL ni lógica de acceso a datos.

| Método | Ruta | Rol requerido | Controlador | Descripción |
|---|---|---|---|---|
| GET / POST | `/login` | Público | `auth_controller.login` | Inicio de sesión. |
| GET | `/auth/login` | Público | `auth_controller.login_legacy` | Redirección compatible hacia `/login`. |
| POST | `/logout` | Usuario autenticado | `auth_controller.logout` | Cierra sesión. |
| GET | `/` | Usuario autenticado | `home_controller.index` | Panel principal del sistema. |
| GET | `/pacientes` | `ADMINISTRADOR`, `RECEPCIONISTA` | `paciente_controller.index` | Lista pacientes y permite búsqueda. |
| GET / POST | `/pacientes/nuevo` | `ADMINISTRADOR`, `RECEPCIONISTA` | `paciente_controller.nuevo` | Registra paciente. |
| GET / POST | `/pacientes/<id_paciente>/editar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `paciente_controller.editar` | Edita paciente existente. |
| GET | `/medicos` | `ADMINISTRADOR` | `medico_controller.index` | Lista médicos y especialidades. |
| GET / POST | `/medicos/nuevo` | `ADMINISTRADOR` | `medico_controller.nuevo` | Registra médico y usuario asociado. |
| GET / POST | `/medicos/<id_medico>/editar` | `ADMINISTRADOR` | `medico_controller.editar` | Edita médico y administra horarios. |
| POST | `/especialidades/nuevo` | `ADMINISTRADOR` | `medico_controller.crear_especialidad` | Crea especialidad. |
| POST | `/medicos/<id_medico>/horarios/nuevo` | `ADMINISTRADOR` | `medico_controller.crear_horario` | Registra horario médico. |
| POST | `/horarios/<id_horario>/estado` | `ADMINISTRADOR` | `medico_controller.actualizar_estado_horario` | Cambia estado de horario. |
| GET | `/medicos/<id_medico>/disponibilidad` | `ADMINISTRADOR` | `medico_controller.disponibilidad` | Devuelve disponibilidad del médico en JSON. |
| GET | `/citas` | `ADMINISTRADOR`, `RECEPCIONISTA`, `MEDICO` | `cita_controller.index` | Lista citas y acciones según rol. |
| GET / POST | `/citas/programar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.programar` | Programa una cita validando disponibilidad. |
| POST | `/citas/<id_cita>/cancelar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.cancelar` | Cancela cita con motivo. |
| POST | `/citas/<id_cita>/notificar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.notificar` | Marca cita como notificada. |
| GET / POST | `/citas/<id_cita>/reprogramar` | `ADMINISTRADOR`, `RECEPCIONISTA` | `cita_controller.reprogramar` | Crea nueva cita y marca la original como reprogramada. |
| POST | `/citas/<id_cita>/atender` | `ADMINISTRADOR`, `MEDICO` | `cita_controller.atender` | Registra atención e historial desde cita. |
| POST | `/citas/<id_cita>/no-asistio` | `ADMINISTRADOR`, `MEDICO` | `cita_controller.marcar_no_asistio` | Marca cita como no asistida. |
| GET | `/historial` | `ADMINISTRADOR`, `MEDICO`, `RECEPCIONISTA` | `historial_controller.index` | Lista historiales de atención. |
| GET / POST | `/historial/cita/<id_cita>/nuevo` | `ADMINISTRADOR`, `MEDICO` | `historial_controller.nuevo_desde_cita` | Crea historial desde una cita existente. |
| GET | `/reportes/citas` | `ADMINISTRADOR` | `reporte_controller.citas` | Reporte básico con filtros por estado, médico y fechas. |

## Endpoints de error

Los manejadores globales renderizan mensajes amigables para `403`, `404` y `500`, registrando el detalle técnico en logs cuando corresponde.
