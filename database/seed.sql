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
