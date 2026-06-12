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
    ('Medicina General', 'Atencion medica integral de primer contacto'),
    ('Pediatria', 'Atencion medica para ninos y adolescentes'),
    ('Cardiologia', 'Diagnostico y tratamiento de enfermedades cardiovasculares'),
    ('Dermatologia', 'Atencion de enfermedades de la piel'),
    ('Ginecologia', 'Atencion integral de salud femenina'),
    ('Traumatologia', 'Diagnostico y tratamiento de lesiones oseas y musculares')
ON DUPLICATE KEY UPDATE
    descripcion = VALUES(descripcion);

UPDATE medico m
INNER JOIN especialidad anterior
    ON anterior.id_especialidad = m.id_especialidad
INNER JOIN especialidad normalizada
    ON normalizada.nombre = 'Pediatria'
SET m.id_especialidad = normalizada.id_especialidad
WHERE anterior.nombre <> 'Pediatria'
  AND anterior.nombre LIKE 'Pediatr%';

UPDATE medico m
INNER JOIN especialidad anterior
    ON anterior.id_especialidad = m.id_especialidad
INNER JOIN especialidad normalizada
    ON normalizada.nombre = 'Cardiologia'
SET m.id_especialidad = normalizada.id_especialidad
WHERE anterior.nombre <> 'Cardiologia'
  AND anterior.nombre LIKE 'Cardiolog%';

DELETE anterior
FROM especialidad anterior
LEFT JOIN medico m
    ON m.id_especialidad = anterior.id_especialidad
WHERE anterior.nombre <> 'Pediatria'
  AND anterior.nombre LIKE 'Pediatr%'
  AND m.id_medico IS NULL;

DELETE anterior
FROM especialidad anterior
LEFT JOIN medico m
    ON m.id_especialidad = anterior.id_especialidad
WHERE anterior.nombre <> 'Cardiologia'
  AND anterior.nombre LIKE 'Cardiolog%'
  AND m.id_medico IS NULL;

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
    'Luis Alberto',
    'Quispe Mamani',
    'luis.quispe.mamani@gmail.com'
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
    'CMP-145872'
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
VALUES
    (
        'ana.huaman',
        'pbkdf2:sha256:1000000$demo_medico_salt$66f30174d0d6605ff86c30e50dec01f5d00a43a0a119e59be4fe56ddf2b8181d',
        'MEDICO',
        'ACTIVO',
        'Ana Lucia',
        'Huaman Flores',
        'ana.huaman.flores@gmail.com'
    ),
    (
        'carlos.choque',
        'pbkdf2:sha256:1000000$demo_medico_salt$66f30174d0d6605ff86c30e50dec01f5d00a43a0a119e59be4fe56ddf2b8181d',
        'MEDICO',
        'ACTIVO',
        'Carlos Enrique',
        'Choque Rojas',
        'carlos.choque.rojas@gmail.com'
    ),
    (
        'rosa.condori',
        'pbkdf2:sha256:1000000$demo_medico_salt$66f30174d0d6605ff86c30e50dec01f5d00a43a0a119e59be4fe56ddf2b8181d',
        'MEDICO',
        'ACTIVO',
        'Rosa Maria',
        'Condori Salazar',
        'rosa.condori.salazar@gmail.com'
    ),
    (
        'miguel.torres',
        'pbkdf2:sha256:1000000$demo_medico_salt$66f30174d0d6605ff86c30e50dec01f5d00a43a0a119e59be4fe56ddf2b8181d',
        'MEDICO',
        'ACTIVO',
        'Miguel Angel',
        'Torres Paredes',
        'miguel.torres.paredes@gmail.com'
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
    'CMP-258963'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Cardiologia'
WHERE usuario_sistema.username = 'ana.huaman'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO medico (id_usuario, id_especialidad, numero_colegiatura)
SELECT
    usuario_sistema.id_usuario,
    especialidad.id_especialidad,
    'CMP-369741'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Pediatria'
WHERE usuario_sistema.username = 'carlos.choque'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO medico (id_usuario, id_especialidad, numero_colegiatura)
SELECT
    usuario_sistema.id_usuario,
    especialidad.id_especialidad,
    'CMP-481256'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Dermatologia'
WHERE usuario_sistema.username = 'rosa.condori'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO medico (id_usuario, id_especialidad, numero_colegiatura)
SELECT
    usuario_sistema.id_usuario,
    especialidad.id_especialidad,
    'CMP-592374'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Traumatologia'
WHERE usuario_sistema.username = 'miguel.torres'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO horario (
    id_medico,
    fecha,
    hora_inicio,
    hora_fin,
    estado
)
SELECT
    m.id_medico,
    '2026-06-15',
    '08:00:00',
    '12:00:00',
    'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'medico'
ON DUPLICATE KEY UPDATE
    estado = VALUES(estado);

INSERT INTO horario (
    id_medico,
    fecha,
    hora_inicio,
    hora_fin,
    estado
)
SELECT
    m.id_medico,
    '2026-06-15',
    '09:00:00',
    '13:00:00',
    'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'ana.huaman'
ON DUPLICATE KEY UPDATE
    estado = VALUES(estado);

INSERT INTO horario (
    id_medico,
    fecha,
    hora_inicio,
    hora_fin,
    estado
)
SELECT
    m.id_medico,
    '2026-06-16',
    '08:00:00',
    '12:00:00',
    'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'carlos.choque'
ON DUPLICATE KEY UPDATE
    estado = VALUES(estado);

INSERT INTO horario (
    id_medico,
    fecha,
    hora_inicio,
    hora_fin,
    estado
)
SELECT
    m.id_medico,
    '2026-06-16',
    '14:00:00',
    '18:00:00',
    'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'rosa.condori'
ON DUPLICATE KEY UPDATE
    estado = VALUES(estado);

INSERT INTO horario (
    id_medico,
    fecha,
    hora_inicio,
    hora_fin,
    estado
)
SELECT
    m.id_medico,
    '2026-06-17',
    '10:00:00',
    '14:00:00',
    'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'miguel.torres'
ON DUPLICATE KEY UPDATE
    estado = VALUES(estado);

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

INSERT INTO paciente (
    dni,
    nombres,
    apellidos,
    telefono,
    email,
    fecha_nacimiento,
    direccion
)
VALUES
    (
        '45879632',
        'Maria Elena',
        'Vargas Huaman',
        '987654321',
        'maria.vargas.huaman@paciente.test',
        '1990-04-12',
        'Av. Tupac Amaru 1245, Comas'
    ),
    (
        '72651489',
        'Jose Antonio',
        'Ramos Quispe',
        '956123478',
        'jose.ramos.quispe@paciente.test',
        '1985-09-23',
        'Jr. Los Pinos 342, Comas'
    ),
    (
        '60473821',
        'Carmen Rosa',
        'Mamani Flores',
        '914785236',
        'carmen.mamani.flores@paciente.test',
        '1978-01-30',
        'Av. Universitaria 875, Los Olivos'
    ),
    (
        '73591246',
        'Diego Alonso',
        'Salazar Torres',
        '998741256',
        'diego.salazar.torres@paciente.test',
        '2001-07-18',
        'Calle Las Gardenias 210, Carabayllo'
    ),
    (
        '68954127',
        'Lucia Fernanda',
        'Condori Rojas',
        '943216587',
        'lucia.condori.rojas@paciente.test',
        '1996-11-05',
        'Pasaje San Martin 456, Comas'
    ),
    (
        '51247896',
        'Juan Carlos',
        'Paredes Choque',
        '965874123',
        'juan.paredes.choque@paciente.test',
        '1969-03-14',
        'Av. Mexico 781, Independencia'
    )
ON DUPLICATE KEY UPDATE
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    telefono = VALUES(telefono),
    email = VALUES(email),
    fecha_nacimiento = VALUES(fecha_nacimiento),
    direccion = VALUES(direccion);

INSERT INTO cita (
    id_paciente,
    id_medico,
    id_recepcionista,
    fecha,
    hora,
    estado,
    motivo_consulta,
    notificado,
    fecha_notificacion
)
SELECT
    p.id_paciente,
    m.id_medico,
    r.id_recepcionista,
    '2026-05-20',
    '09:00:00',
    'ATENDIDA',
    'Dolor de cabeza recurrente',
    TRUE,
    '2026-05-19 10:30:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'medico'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'recepcionista'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '45879632'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-05-20'
        AND c.hora = '09:00:00'
  );

INSERT INTO cita (
    id_paciente,
    id_medico,
    id_recepcionista,
    fecha,
    hora,
    estado,
    motivo_consulta,
    notificado,
    fecha_notificacion
)
SELECT
    p.id_paciente,
    m.id_medico,
    r.id_recepcionista,
    '2026-05-21',
    '10:00:00',
    'ATENDIDA',
    'Control pediatrico general',
    TRUE,
    '2026-05-20 11:15:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'carlos.choque'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'recepcionista'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '73591246'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-05-21'
        AND c.hora = '10:00:00'
  );

INSERT INTO cita (
    id_paciente,
    id_medico,
    id_recepcionista,
    fecha,
    hora,
    estado,
    motivo_consulta,
    notificado,
    fecha_notificacion
)
SELECT
    p.id_paciente,
    m.id_medico,
    r.id_recepcionista,
    '2026-05-22',
    '15:30:00',
    'ATENDIDA',
    'Evaluacion de lesion en piel',
    TRUE,
    '2026-05-21 09:45:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'rosa.condori'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'recepcionista'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '60473821'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-05-22'
        AND c.hora = '15:30:00'
  );

INSERT INTO historial_cita (
    id_cita,
    diagnostico,
    tratamiento,
    observaciones,
    fecha_atencion
)
SELECT
    c.id_cita,
    'Cefalea tensional',
    'Hidratacion, descanso y analgesico indicado',
    'Paciente estable. Se recomienda control si persisten molestias.',
    '2026-05-20 09:25:00'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '45879632'
  AND um.username = 'medico'
  AND c.fecha = '2026-05-20'
  AND c.hora = '09:00:00'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );

INSERT INTO historial_cita (
    id_cita,
    diagnostico,
    tratamiento,
    observaciones,
    fecha_atencion
)
SELECT
    c.id_cita,
    'Control pediatrico sin signos de alarma',
    'Indicaciones preventivas y seguimiento rutinario',
    'Paciente con evolucion favorable.',
    '2026-05-21 10:30:00'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '73591246'
  AND um.username = 'carlos.choque'
  AND c.fecha = '2026-05-21'
  AND c.hora = '10:00:00'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );

INSERT INTO historial_cita (
    id_cita,
    diagnostico,
    tratamiento,
    observaciones,
    fecha_atencion
)
SELECT
    c.id_cita,
    'Dermatitis leve',
    'Tratamiento topico y control en dos semanas',
    'Se indican cuidados de piel y evitar irritantes.',
    '2026-05-22 16:00:00'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '60473821'
  AND um.username = 'rosa.condori'
  AND c.fecha = '2026-05-22'
  AND c.hora = '15:30:00'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );
