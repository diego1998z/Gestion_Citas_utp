CREATE DATABASE IF NOT EXISTS gestion_citas_medicas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gestion_citas_medicas;

CREATE TABLE IF NOT EXISTS usuario_sistema (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('ADMINISTRADOR', 'RECEPCIONISTA', 'MEDICO') NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(120) NULL,
    telefono VARCHAR(20) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_sistema_username UNIQUE (username),
    CONSTRAINT uq_usuario_sistema_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrador (
    id_administrador INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_administrador_id_usuario UNIQUE (id_usuario),
    CONSTRAINT fk_administrador_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario_sistema (id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recepcionista (
    id_recepcionista INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    codigo_empleado VARCHAR(30) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_recepcionista_id_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_recepcionista_codigo_empleado UNIQUE (codigo_empleado),
    CONSTRAINT fk_recepcionista_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario_sistema (id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS especialidad (
    id_especialidad INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_especialidad_nombre UNIQUE (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS medico (
    id_medico INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    id_especialidad INT UNSIGNED NOT NULL,
    numero_colegiatura VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_medico_id_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_medico_numero_colegiatura UNIQUE (numero_colegiatura),
    CONSTRAINT fk_medico_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario_sistema (id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_medico_especialidad
        FOREIGN KEY (id_especialidad) REFERENCES especialidad (id_especialidad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS horario (
    id_horario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_medico INT UNSIGNED NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado ENUM('DISPONIBLE', 'NO_DISPONIBLE') NOT NULL DEFAULT 'DISPONIBLE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_horario_medico_fecha_hora UNIQUE (id_medico, fecha, hora_inicio, hora_fin),
    CONSTRAINT chk_horario_rango CHECK (hora_inicio < hora_fin),
    CONSTRAINT fk_horario_medico
        FOREIGN KEY (id_medico) REFERENCES medico (id_medico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX idx_horario_medico_fecha (id_medico, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS paciente (
    id_paciente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(15) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NULL,
    email VARCHAR(120) NULL,
    fecha_nacimiento DATE NULL,
    direccion VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_paciente_dni UNIQUE (dni),
    CONSTRAINT uq_paciente_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cita (
    id_cita INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT UNSIGNED NOT NULL,
    id_medico INT UNSIGNED NOT NULL,
    id_recepcionista INT UNSIGNED NULL,
    id_cita_origen INT UNSIGNED NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado ENUM(
        'PENDIENTE',
        'CONFIRMADA',
        'CANCELADA',
        'ATENDIDA',
        'NO_ASISTIO',
        'REPROGRAMADA'
    ) NOT NULL DEFAULT 'PENDIENTE',
    cita_activa TINYINT GENERATED ALWAYS AS (
        CASE
            WHEN estado IN ('PENDIENTE', 'CONFIRMADA') THEN 1
            ELSE NULL
        END
    ) STORED,
    motivo_consulta VARCHAR(255) NULL,
    motivo_cancelacion VARCHAR(255) NULL,
    fecha_cancelacion DATETIME NULL,
    notificado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_notificacion DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_cita_medico_fecha_hora_activa UNIQUE (id_medico, fecha, hora, cita_activa),
    CONSTRAINT fk_cita_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente (id_paciente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_cita_medico
        FOREIGN KEY (id_medico) REFERENCES medico (id_medico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_cita_recepcionista
        FOREIGN KEY (id_recepcionista) REFERENCES recepcionista (id_recepcionista)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_cita_origen
        FOREIGN KEY (id_cita_origen) REFERENCES cita (id_cita)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX idx_cita_medico_fecha_hora_estado (id_medico, fecha, hora, estado),
    INDEX idx_cita_paciente_fecha (id_paciente, fecha),
    INDEX idx_cita_estado_fecha (estado, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS historial_cita (
    id_historial_cita INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_cita INT UNSIGNED NOT NULL,
    diagnostico TEXT NOT NULL,
    tratamiento TEXT NULL,
    observaciones TEXT NULL,
    fecha_atencion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_historial_cita_id_cita UNIQUE (id_cita),
    CONSTRAINT fk_historial_cita_cita
        FOREIGN KEY (id_cita) REFERENCES cita (id_cita)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cita_evento (
    id_cita_evento INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_cita INT UNSIGNED NOT NULL,
    id_usuario_actor INT UNSIGNED NULL,
    id_cita_relacionada INT UNSIGNED NULL,
    tipo_evento ENUM('CONFIRMADA', 'REPROGRAMADA', 'CANCELADA', 'NOTIFICADA', 'NOTIFICACION_FALLIDA', 'SEGUIMIENTO_CREADO', 'ATENDIDA', 'NO_ASISTIO') NOT NULL,
    fecha_anterior DATE NULL,
    hora_anterior TIME NULL,
    fecha_nueva DATE NULL,
    hora_nueva TIME NULL,
    motivo VARCHAR(255) NULL,
    detalle VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cita_evento_cita
        FOREIGN KEY (id_cita) REFERENCES cita (id_cita)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_cita_evento_actor
        FOREIGN KEY (id_usuario_actor) REFERENCES usuario_sistema (id_usuario)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_cita_evento_relacionada
        FOREIGN KEY (id_cita_relacionada) REFERENCES cita (id_cita)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    INDEX idx_cita_evento_cita_fecha (id_cita, created_at),
    INDEX idx_cita_evento_tipo_fecha (tipo_evento, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
