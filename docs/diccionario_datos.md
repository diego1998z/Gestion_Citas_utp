# Diccionario de datos

Base de datos: `gestion_citas_medicas`  
Motor esperado: InnoDB  
Convención: tablas en singular, campos en `snake_case`, PK con formato `id_tabla`.

## usuario_sistema

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_usuario | INT UNSIGNED PK AI | Identificador del usuario del sistema. |
| username | VARCHAR(50) | Único, usado para login. |
| password_hash | VARCHAR(255) | Hash seguro de contraseña; no guardar texto plano. |
| rol | ENUM | `ADMINISTRADOR`, `RECEPCIONISTA`, `MEDICO`. |
| estado | ENUM | `ACTIVO`, `INACTIVO`. |
| nombres | VARCHAR(100) | Nombres del usuario. |
| apellidos | VARCHAR(100) | Apellidos del usuario. |
| email | VARCHAR(120) | Único, opcional. |
| telefono | VARCHAR(20) | Opcional. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## administrador

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_administrador | INT UNSIGNED PK AI | Identificador del perfil administrador. |
| id_usuario | INT UNSIGNED FK UNIQUE | Relación 1 a 1 con `usuario_sistema`. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## recepcionista

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_recepcionista | INT UNSIGNED PK AI | Identificador del perfil recepcionista. |
| id_usuario | INT UNSIGNED FK UNIQUE | Relación 1 a 1 con `usuario_sistema`. |
| codigo_empleado | VARCHAR(30) | Código interno único, opcional. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## especialidad

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_especialidad | INT UNSIGNED PK AI | Identificador de especialidad. |
| nombre | VARCHAR(100) | Único, obligatorio. |
| descripcion | VARCHAR(255) | Descripción opcional. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## medico

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_medico | INT UNSIGNED PK AI | Identificador del médico. |
| id_usuario | INT UNSIGNED FK UNIQUE | Relación 1 a 1 con `usuario_sistema`. |
| id_especialidad | INT UNSIGNED FK | Especialidad del médico. |
| numero_colegiatura | VARCHAR(30) | Único, obligatorio. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## horario

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_horario | INT UNSIGNED PK AI | Identificador de horario. |
| id_medico | INT UNSIGNED FK | Médico asociado. |
| fecha | DATE | Día de atención. |
| hora_inicio | TIME | Inicio del bloque. |
| hora_fin | TIME | Fin del bloque; debe ser mayor a `hora_inicio`. |
| estado | ENUM | `DISPONIBLE`, `NO_DISPONIBLE`. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

Regla: existe unicidad por `id_medico`, `fecha`, `hora_inicio`, `hora_fin`.

## paciente

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_paciente | INT UNSIGNED PK AI | Identificador del paciente. |
| dni | VARCHAR(15) | Único, obligatorio. |
| nombres | VARCHAR(100) | Nombres del paciente. |
| apellidos | VARCHAR(100) | Apellidos del paciente. |
| telefono | VARCHAR(20) | Opcional. |
| email | VARCHAR(120) | Único, opcional. |
| fecha_nacimiento | DATE | Opcional. |
| direccion | VARCHAR(255) | Opcional. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## cita

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_cita | INT UNSIGNED PK AI | Identificador de la cita. |
| id_paciente | INT UNSIGNED FK | Paciente citado. |
| id_medico | INT UNSIGNED FK | Médico que atenderá. |
| id_recepcionista | INT UNSIGNED FK NULL | Recepcionista que programó, si aplica. |
| id_cita_origen | INT UNSIGNED FK NULL | Cita original al reprogramar. |
| fecha | DATE | Fecha de la cita. |
| hora | TIME | Hora de la cita. |
| estado | ENUM | `PENDIENTE`, `CONFIRMADA`, `CANCELADA`, `ATENDIDA`, `NO_ASISTIO`, `REPROGRAMADA`. |
| cita_activa | TINYINT GENERATED | Permite unicidad sólo para citas activas. |
| motivo_consulta | VARCHAR(255) | Motivo registrado al programar. |
| motivo_cancelacion | VARCHAR(255) | Obligatorio a nivel de flujo al cancelar. |
| fecha_cancelacion | DATETIME | Fecha/hora de cancelación. |
| notificado | BOOLEAN | Indica si el paciente fue notificado. |
| fecha_notificacion | DATETIME | Fecha/hora de notificación. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

Regla crítica: índice único `id_medico`, `fecha`, `hora`, `cita_activa` evita doble reserva activa para el mismo médico.

## historial_cita

| Campo | Tipo | Regla / descripción |
|---|---|---|
| id_historial_cita | INT UNSIGNED PK AI | Identificador del historial. |
| id_cita | INT UNSIGNED FK UNIQUE | Cita atendida. No se duplica `id_paciente`. |
| diagnostico | TEXT | Diagnóstico u observación principal. |
| tratamiento | TEXT | Tratamiento indicado, opcional. |
| observaciones | TEXT | Observaciones adicionales, opcional. |
| fecha_atencion | DATETIME | Fecha/hora de atención. |
| created_at / updated_at | TIMESTAMP | Auditoría. |

## Relaciones principales

- `usuario_sistema` 1 a 0..1 `administrador`.
- `usuario_sistema` 1 a 0..1 `recepcionista`.
- `usuario_sistema` 1 a 0..1 `medico`.
- `especialidad` 1 a muchos `medico`.
- `medico` 1 a muchos `horario`.
- `paciente` 1 a muchos `cita`.
- `medico` 1 a muchos `cita`.
- `recepcionista` 1 a muchos `cita`.
- `cita` 1 a 0..1 `historial_cita`.
