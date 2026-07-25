# Manual de usuario

## 1. Acceso al sistema

1. Abrir la URL del sistema en el navegador.
2. Seleccionar el rol visual correspondiente: Administrador, Médico o Recepcionista.
3. Ingresar usuario y contraseña.
4. Presionar **Ingresar**.

Si las credenciales, el estado del usuario o el rol seleccionado no coinciden, el sistema mostrará un mensaje amigable y permitirá intentar nuevamente.

## 2. Administrador

El administrador puede gestionar la configuración general y consultar reportes.

### Gestionar pacientes

1. Entrar a **Pacientes**.
2. Usar el buscador para ubicar un paciente existente.
3. Presionar **Nuevo paciente** para registrar uno.
4. Completar DNI, nombres, apellidos y datos de contacto.
5. Guardar.
6. Si el DNI ya existe, el sistema mostrará el error correspondiente.

### Gestionar médicos

1. Entrar a **Médicos**.
2. Presionar **Nuevo médico**.
3. Completar datos personales, usuario, correo, colegiatura y especialidad.
4. Guardar.
5. Para modificar información, usar la opción **Editar** del listado.

### Gestionar especialidades

1. Entrar a **Médicos**.
2. En el panel de especialidades, escribir el nombre de la nueva especialidad.
3. Guardar.

### Gestionar horarios

1. Editar un médico.
2. En la sección de horarios, cargar fecha, hora de inicio y hora de fin.
3. Guardar horario.
4. Usar **Activar** o **Desactivar** para cambiar disponibilidad.

### Consultar reportes

1. Entrar a **Reportes**.
2. Filtrar por estado, médico o rango de fechas.
3. Revisar el resumen y el detalle de citas.

## 3. Recepcionista

La recepcionista opera el flujo diario de atención administrativa.

### Registrar pacientes

1. Entrar a **Pacientes**.
2. Presionar **Nuevo paciente**.
3. Completar la ficha.
4. Guardar.

### Programar una cita

1. Entrar a **Citas**.
2. Presionar **Programar cita**.
3. Seleccionar paciente y médico.
4. Elegir fecha, hora y motivo.
5. Guardar.

El sistema valida disponibilidad del médico y bloquea dos citas activas para el mismo médico, fecha y hora.

### Confirmar una cita

1. Entrar a **Citas**.
2. Buscar una cita en estado `PENDIENTE`.
3. Presionar **Confirmar**.

El sistema cambia la cita a `CONFIRMADA`. Si la cita ya estaba confirmada o tiene un estado final como `CANCELADA`, `ATENDIDA`, `NO_ASISTIO` o `REPROGRAMADA`, muestra un mensaje claro y no modifica el registro.

### Cancelar una cita

1. Entrar a **Citas**.
2. Buscar la cita activa.
3. Escribir el motivo de cancelación.
4. Presionar **Cancelar**.

### Reprogramar una cita

1. Entrar a **Citas**.
2. Presionar **Reprogramar** en la cita deseada.
3. Elegir nuevo médico, fecha, hora y motivo.
4. Guardar.

La cita original queda como `REPROGRAMADA` y se crea una nueva cita pendiente.

### Notificar al paciente

Antes de usar esta opción, el administrador técnico debe configurar el proveedor de correo. En local puede usarse SMTP con Gmail y App Password. En Railway se recomienda Brevo por API HTTPS configurando `EMAIL_PROVIDER=brevo` y las variables de Brevo en el panel de Railway.

1. Entrar a **Citas**.
2. Buscar una cita no notificada.
3. Presionar **Notificar**.
4. Si el correo se envía correctamente, la cita queda marcada como notificada.

## 4. Médico

El médico trabaja sobre sus propias citas e historiales.

### Consultar citas

1. Entrar a **Citas**.
2. Revisar las citas asignadas.
3. Usar el buscador si hace falta ubicar un paciente o motivo.

### Registrar atención

1. Desde una cita activa, presionar la acción para crear historial o registrar atención.
2. Completar observación clínica.
3. Guardar.

El sistema marca la cita como `ATENDIDA` y evita duplicar historial para la misma cita.

### Marcar no asistencia

1. Entrar a **Citas**.
2. Buscar la cita activa.
3. Presionar **No asistió**.

### Consultar historial

1. Entrar a **Historial**.
2. Buscar por paciente, médico o diagnóstico/observación.
3. Revisar la atención registrada.

## 5. Mensajes y errores frecuentes

| Situación | Qué significa | Qué hacer |
|---|---|---|
| Credenciales inválidas | Usuario, contraseña o rol incorrecto. | Revisar datos e intentar nuevamente. |
| Acceso denegado | El rol no tiene permiso para esa pantalla. | Ingresar con un rol autorizado. |
| DNI duplicado | Ya existe un paciente con ese DNI. | Buscar el paciente y editarlo si corresponde. |
| Horario no disponible | El médico no atiende o ya tiene cita activa en ese horario. | Elegir otro horario o médico. |
| Formulario vencido o inválido | El token de seguridad CSRF expiró o falta. | Recargar la página y reenviar el formulario. |

## 6. Buenas prácticas de uso

- No compartir credenciales.
- Cerrar sesión al terminar.
- Revisar bien fecha y hora antes de confirmar una cita.
- Registrar motivos de cancelación claros.
- No incluir información sensible innecesaria en observaciones clínicas.
