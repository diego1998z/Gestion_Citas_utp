# Checklist de validación y manual técnico mínimo

Este documento guía una revisión manual del MVP sin exponer SQL interno al usuario final.

## Preparación

- [ ] Crear entorno virtual e instalar `requirements.txt`.
- [ ] Copiar `.env.example` a `.env` y configurar credenciales MySQL.
- [ ] Ejecutar `database/schema.sql`.
- [ ] Ejecutar `database/seed.sql`.
- [ ] Confirmar que `logs/app.log` existe o se crea al iniciar la app.

## Validación de seguridad

- [ ] Iniciar sesión con usuario demo `admin`.
- [ ] Probar credenciales incorrectas y confirmar mensaje amigable.
- [ ] Confirmar que rutas protegidas redirigen o bloquean cuando no hay sesión.
- [ ] Confirmar que rutas de administración no están disponibles para roles no autorizados.
- [ ] Verificar que las contraseñas no aparecen en texto plano en vistas ni documentación operativa.
- [ ] Enviar un POST sin `csrf_token` y confirmar respuesta 403 amigable.
- [ ] Confirmar que `SECRET_KEY` está definida antes de usar entorno `production`.

## Validación MVC

- [ ] Revisar que los templates en `app/views/` no contienen consultas SQL.
- [ ] Confirmar que las consultas están en `app/models/`.
- [ ] Confirmar que los controladores validan formularios y coordinan modelos/vistas.
- [ ] Confirmar que operaciones críticas muestran mensajes amigables y registran detalle técnico en logs.

## Flujo pacientes

- [ ] Listar pacientes.
- [ ] Registrar paciente nuevo con DNI único.
- [ ] Intentar registrar DNI duplicado y confirmar mensaje amigable.
- [ ] Editar datos de contacto del paciente.

## Flujo médicos, especialidades y horarios

- [ ] Crear una especialidad.
- [ ] Registrar médico con usuario asociado y número de colegiatura único.
- [ ] Agregar horario disponible para el médico.
- [ ] Cambiar horario a `NO_DISPONIBLE` y volver a `DISPONIBLE`.
- [ ] Consultar disponibilidad del médico desde la ruta JSON documentada.

## Flujo citas

- [ ] Programar cita seleccionando paciente, médico, fecha, hora y motivo.
- [ ] Intentar programar una segunda cita activa para el mismo médico, fecha y hora; debe bloquearse.
- [ ] Notificar al paciente y verificar que aparece como notificado.
- [ ] Cancelar una cita activa registrando motivo de cancelación.
- [ ] Reprogramar una cita activa; la cita original debe quedar `REPROGRAMADA` y debe crearse una nueva `PENDIENTE`.
- [ ] Marcar una cita como `NO_ASISTIO` desde rol permitido.

## Flujo historial

- [ ] Desde una cita activa, registrar atención/historial.
- [ ] Confirmar que la cita queda `ATENDIDA`.
- [ ] Confirmar que la cita no permite duplicar historial.
- [ ] Listar historial y verificar datos de paciente, médico y especialidad.

## Reporte de citas

- [ ] Ingresar como `ADMINISTRADOR`.
- [ ] Abrir `/reportes/citas` desde el sidebar.
- [ ] Filtrar por estado.
- [ ] Filtrar por médico.
- [ ] Filtrar por rango de fechas.
- [ ] Confirmar que la tabla y el resumen por estado cambian según los filtros.
- [ ] Confirmar que el botón de exportación es visual y queda pendiente para una mejora posterior.

## Validación técnica permitida sin build

```powershell
python -m py_compile app/__init__.py config/settings.py app/controllers/*.py app/models/*.py app/utils/*.py
git diff --check
```

Además, inspeccionar templates para confirmar que no aparezcan `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `mysql` ni `get_cursor` dentro de `app/views/`.

## Pendientes recomendados

- Diseñar frontend final de reportes con gráficos simples por estado y especialidad.
- Agregar exportación real PDF/Excel si el profesor la solicita.
- Reemplazar datos temporales del dashboard por consultas reales de indicadores.
- Crear manual de usuario extendido con capturas cuando la UI quede cerrada.
