USE gestion_citas_medicas;

INSERT INTO usuario_sistema (
    username,
    password_hash,
    rol,
    estado,
    nombres,
    apellidos,
    email
)
VALUES (
    'admin',
    'pbkdf2:sha256:1000000$demo_admin_salt$e62919f43637326188dc4db52aece55e55d4c5d812ad7684a85e99d7bdbcf8fd',
    'ADMINISTRADOR',
    'ACTIVO',
    'Admin',
    'Demo',
    'admin.demo@clinica.test'
)
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO administrador (id_usuario)
SELECT id_usuario
FROM usuario_sistema
WHERE username = 'admin'
ON DUPLICATE KEY UPDATE
    id_usuario = VALUES(id_usuario);

INSERT INTO especialidad (nombre, descripcion)
VALUES
    ('Medicina General', 'Atención médica integral de primer contacto'),
    ('Pediatría', 'Atención médica para niños y adolescentes'),
    ('Cardiología', 'Diagnóstico y tratamiento de enfermedades cardiovasculares')
ON DUPLICATE KEY UPDATE
    descripcion = VALUES(descripcion);

INSERT INTO usuario_sistema (
    username,
    password_hash,
    rol,
    estado,
    nombres,
    apellidos,
    email
)
VALUES (
    'medico',
    'pbkdf2:sha256:1000000$demo_medico_salt$66f30174d0d6605ff86c30e50dec01f5d00a43a0a119e59be4fe56ddf2b8181d',
    'MEDICO',
    'ACTIVO',
    'Médico',
    'Demo',
    'medico.demo@clinica.test'
)
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO medico (id_usuario, id_especialidad, numero_colegiatura)
SELECT
    usuario_sistema.id_usuario,
    especialidad.id_especialidad,
    'CMP-DEMO-001'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Medicina General'
WHERE usuario_sistema.username = 'medico'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO usuario_sistema (
    username,
    password_hash,
    rol,
    estado,
    nombres,
    apellidos,
    email
)
VALUES (
    'recepcionista',
    'pbkdf2:sha256:1000000$demo_recepcionista_salt$6d63b5f227a6116d83e5bc07036db00acd34ba908301e77c164a316822218d38',
    'RECEPCIONISTA',
    'ACTIVO',
    'Recepcionista',
    'Demo',
    'recepcionista.demo@clinica.test'
)
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO recepcionista (id_usuario, codigo_empleado)
SELECT
    id_usuario,
    'REC-DEMO-001'
FROM usuario_sistema
WHERE username = 'recepcionista'
ON DUPLICATE KEY UPDATE
    codigo_empleado = VALUES(codigo_empleado);
