USE gestion_citas_medicas;

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

ALTER TABLE cita_evento
    MODIFY tipo_evento ENUM('CONFIRMADA', 'REPROGRAMADA', 'CANCELADA', 'NOTIFICADA', 'NOTIFICACION_FALLIDA', 'SEGUIMIENTO_CREADO', 'ATENDIDA', 'NO_ASISTIO') NOT NULL;
