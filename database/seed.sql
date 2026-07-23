USE gestion_citas_medicas;

-- Normaliza credenciales demo antiguas a usernames ligados a nombres reales.
UPDATE usuario_sistema
SET username = 'patricia.salas'
WHERE username = 'admin'
  AND NOT EXISTS (
      SELECT 1 FROM (SELECT id_usuario FROM usuario_sistema WHERE username = 'patricia.salas') AS usuario_existente
  );

UPDATE usuario_sistema
SET username = 'luis.quispe'
WHERE username = 'medico'
  AND NOT EXISTS (
      SELECT 1 FROM (SELECT id_usuario FROM usuario_sistema WHERE username = 'luis.quispe') AS usuario_existente
  );

UPDATE usuario_sistema
SET username = 'valeria.nunez'
WHERE username = 'recepcionista'
  AND NOT EXISTS (
      SELECT 1 FROM (SELECT id_usuario FROM usuario_sistema WHERE username = 'valeria.nunez') AS usuario_existente
  );

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
    'patricia.salas',
    'scrypt:32768:8:1$3ork0VoP8SuJcgCd$2c24d013d218ae3d16f09a6f69e062ded54555760b1f2498d583a232a36ee0002a1262821d99eaa6bf6771034beec134e5447849f266e72be8fa92528abd57e6',
    'ADMINISTRADOR',
    'ACTIVO',
    'Patricia Elena',
    'Salas Medina',
    'patricia.salas@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO administrador (id_usuario)
SELECT id_usuario
FROM usuario_sistema
WHERE username = 'patricia.salas'
ON DUPLICATE KEY UPDATE
    id_usuario = VALUES(id_usuario);


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
    'roberto.rivas',
    'scrypt:32768:8:1$pTsfkT01uksDxYL0$adc7f483b84280ad7ee6e05f2aa770bf7ee6b13f805e55f540e16f1beebbc5dbe44333ec8e1490d90fc6be04b27cbf584d91e9e29ebb8b5156551654fa681c60',
    'ADMINISTRADOR',
    'ACTIVO',
    'Roberto Carlos',
    'Rivas Alarcon',
    'roberto.rivas.alarcon@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO administrador (id_usuario)
SELECT id_usuario
FROM usuario_sistema
WHERE username = 'roberto.rivas'
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
    'luis.quispe',
    'scrypt:32768:8:1$HhB91TUBcidImQJk$d37f9e3e5e828e41202dab4f1844037eb0ffc1b43545320bd121e890d33fae7305c3e50012090968ad9c387a0f578aeac17c8cefc8524e7ccbefb4ba817e308a',
    'MEDICO',
    'ACTIVO',
    'Luis Alberto',
    'Quispe Mamani',
    'luis.quispe.mamani@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
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
WHERE usuario_sistema.username = 'luis.quispe'
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
        'scrypt:32768:8:1$AMAhewNOASpQWg9L$ff75ec52451092d4e43b8347e14e39e7a9d4fdc4800efcc5b48814c57eb8130ca827fdd0e8274972addeb13be57df843d965334daf17b547ab9891c9043db98e',
        'MEDICO',
        'ACTIVO',
        'Ana Lucia',
        'Huaman Flores',
        'ana.huaman.flores@demo-clinic.test'
    ),
    (
        'carlos.choque',
        'scrypt:32768:8:1$CoVMOEqBukfalZnx$ed36959b0caebcf556093d69283453ca65613173ce9cfdd3afed441a7f9596cbb3205bdbc1938c68ef4ebd6b8f1f44daf60c397f797a02f246dd0f78a005468f',
        'MEDICO',
        'ACTIVO',
        'Carlos Enrique',
        'Choque Rojas',
        'carlos.choque.rojas@demo-clinic.test'
    ),
    (
        'rosa.condori',
        'scrypt:32768:8:1$zFj6kcqtivv7bQVt$dec361fa1863f25fb89250887714981a7fe5fa72ab0236996fed2845d6159c3e5214966d48b77bb1ea4a7bacefd358513cac4820617ef9f94dc7a2a7b957ceb8',
        'MEDICO',
        'ACTIVO',
        'Rosa Maria',
        'Condori Salazar',
        'rosa.condori.salazar@demo-clinic.test'
    ),
    (
        'miguel.torres',
        'scrypt:32768:8:1$noY5irxJZeg3G4s1$7a0e7f29bc146c8118cacd2ee5591c42ba1fda825ce15820a4547bc9b4874f01ddedb70958ddd5dc84bf663974fa9c85dbf6716a2730a63e26a9bf2ccd910228',
        'MEDICO',
        'ACTIVO',
        'Miguel Angel',
        'Torres Paredes',
        'miguel.torres.paredes@demo-clinic.test'
    )
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
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
WHERE u.username = 'luis.quispe'
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
    'valeria.nunez',
    'scrypt:32768:8:1$N1OdXzA27beLKbFc$2dcc49fb3c32fba4cbc2a58c417295fe1885782180aa779b5cfd00ae31931f76a1f5505917ca5a03fc1f92c4d59506fdadcaf35293be57a9ef7259154e674838',
    'RECEPCIONISTA',
    'ACTIVO',
    'Valeria Milagros',
    'Nuñez Castro',
    'valeria.nunez@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
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
WHERE username = 'valeria.nunez'
ON DUPLICATE KEY UPDATE
    codigo_empleado = VALUES(codigo_empleado);


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
    'marisol.castro',
    'scrypt:32768:8:1$Wa3pYGbY6ptMgMZz$b077fca327c29d53cf104b3ada25ebbc9ba9da8c899741597f722dec5cff314619133213eeaf01d5742b4db96547dd1e2104ad189b42523e7f63e3dc4be9c4f1',
    'RECEPCIONISTA',
    'ACTIVO',
    'Marisol Andrea',
    'Castro Benavides',
    'marisol.castro.benavides@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password_hash = VALUES(password_hash),
    rol = VALUES(rol),
    estado = VALUES(estado),
    nombres = VALUES(nombres),
    apellidos = VALUES(apellidos),
    email = VALUES(email);

INSERT INTO recepcionista (id_usuario, codigo_empleado)
SELECT
    id_usuario,
    'REC-DEMO-002'
FROM usuario_sistema
WHERE username = 'marisol.castro'
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
        '90000001',
        'Sofia Camila',
        'Llanos Paredes',
        '900000001',
        'sofia.llanos.paredes@example.test',
        '1990-04-12',
        'Av. Tupac Amaru 1245, Comas'
    ),
    (
        '90000002',
        'Mateo Alejandro',
        'Vega Cardenas',
        '900000002',
        'mateo.vega.cardenas@example.test',
        '1985-09-23',
        'Jr. Los Pinos 342, Comas'
    ),
    (
        '90000003',
        'Valentina Isabel',
        'Ortega Molina',
        '900000003',
        'valentina.ortega.molina@example.test',
        '1978-01-30',
        'Av. Universitaria 875, Los Olivos'
    ),
    (
        '90000004',
        'Sebastian Nicolas',
        'Campos Aguilar',
        '900000004',
        'sebastian.campos.aguilar@example.test',
        '2001-07-18',
        'Calle Las Gardenias 210, Carabayllo'
    ),
    (
        '90000005',
        'Renata Milagros',
        'Soto Cabrera',
        '900000005',
        'renata.soto.cabrera@example.test',
        '1996-11-05',
        'Pasaje San Martin 456, Comas'
    ),
    (
        '90000006',
        'Gabriel Esteban',
        'Rojas Palomino',
        '900000006',
        'gabriel.rojas.palomino@example.test',
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



-- Horarios demo inmediatos para pruebas del 2026-07-23 al 2026-07-28.
INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, d.fecha, d.hora_inicio, d.hora_fin, 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
INNER JOIN (
    SELECT DATE '2026-07-23' AS fecha, TIME '08:00:00' AS hora_inicio, TIME '12:00:00' AS hora_fin
    UNION ALL SELECT DATE '2026-07-24', TIME '08:00:00', TIME '12:00:00'
    UNION ALL SELECT DATE '2026-07-25', TIME '08:00:00', TIME '12:00:00'
    UNION ALL SELECT DATE '2026-07-26', TIME '08:00:00', TIME '12:00:00'
    UNION ALL SELECT DATE '2026-07-27', TIME '08:00:00', TIME '12:00:00'
    UNION ALL SELECT DATE '2026-07-28', TIME '08:00:00', TIME '12:00:00'
) d
WHERE u.username IN ('luis.quispe', 'ana.huaman', 'carlos.choque', 'rosa.condori', 'miguel.torres', 'elena.villanueva')
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

-- Horarios demo futuros julio/agosto 2026 para programación desde 2026-07-23.
INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, h.fecha, h.hora_inicio, h.hora_fin, h.estado
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
INNER JOIN (
    SELECT 'luis.quispe' AS username, DATE '2026-07-24' AS fecha, TIME '08:00:00' AS hora_inicio, TIME '12:00:00' AS hora_fin, 'DISPONIBLE' AS estado
    UNION ALL SELECT 'luis.quispe', DATE '2026-08-03', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'luis.quispe', DATE '2026-08-17', TIME '08:00:00', TIME '12:00:00', 'NO_DISPONIBLE'
    UNION ALL SELECT 'ana.huaman', DATE '2026-07-27', TIME '09:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'ana.huaman', DATE '2026-08-05', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'ana.huaman', DATE '2026-08-19', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'carlos.choque', DATE '2026-07-28', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'carlos.choque', DATE '2026-08-06', TIME '14:00:00', TIME '18:00:00', 'NO_DISPONIBLE'
    UNION ALL SELECT 'carlos.choque', DATE '2026-08-20', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'rosa.condori', DATE '2026-07-29', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'rosa.condori', DATE '2026-08-10', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'rosa.condori', DATE '2026-08-24', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'miguel.torres', DATE '2026-07-30', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'miguel.torres', DATE '2026-08-12', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'miguel.torres', DATE '2026-08-26', TIME '08:00:00', TIME '12:00:00', 'NO_DISPONIBLE'
    UNION ALL SELECT 'elena.villanueva', DATE '2026-07-31', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'elena.villanueva', DATE '2026-08-14', TIME '14:00:00', TIME '18:00:00', 'DISPONIBLE'
    UNION ALL SELECT 'elena.villanueva', DATE '2026-08-28', TIME '08:00:00', TIME '12:00:00', 'DISPONIBLE'
) h ON h.username = u.username
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

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
INNER JOIN usuario_sistema um ON um.username = 'luis.quispe'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000001'
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
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000004'
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
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000003'
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
WHERE p.dni = '90000001'
  AND um.username = 'luis.quispe'
  AND c.fecha = '2026-05-20'
  AND c.hora = '09:00:00'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );

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
    'elena.villanueva',
    'scrypt:32768:8:1$fKg22RunzPQef4us$380faf257bc9ffeb2e8f07e0fadac07c868236e7ca87fd51cf0947a1f155372e755e422f185c05264bd9bf0a43f8ee9b163b9a3e5eb9ae1facca6aa7e6831188',
    'MEDICO',
    'ACTIVO',
    'Elena Pilar',
    'Villanueva Soto',
    'elena.villanueva.soto@demo-clinic.test'
)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
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
    'CMP-604218'
FROM usuario_sistema
INNER JOIN especialidad
    ON especialidad.nombre = 'Ginecologia'
WHERE usuario_sistema.username = 'elena.villanueva'
ON DUPLICATE KEY UPDATE
    id_especialidad = VALUES(id_especialidad),
    numero_colegiatura = VALUES(numero_colegiatura);

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-27', '08:00:00', '12:00:00', 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'elena.villanueva'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-27', '14:00:00', '18:00:00', 'NO_DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'luis.quispe'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO cita (
    id_paciente,
    id_medico,
    id_recepcionista,
    fecha,
    hora,
    estado,
    motivo_consulta,
    motivo_cancelacion,
    fecha_cancelacion,
    notificado,
    fecha_notificacion
)
SELECT
    p.id_paciente,
    m.id_medico,
    r.id_recepcionista,
    '2026-06-27',
    '08:30:00',
    'CANCELADA',
    'Consulta por dolor lumbar',
    'Paciente solicita cancelar por cruce de horarios',
    '2026-06-26 17:45:00',
    TRUE,
    '2026-06-26 09:10:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'rosa.condori'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000002'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-06-27'
        AND c.hora = '08:30:00'
  );

INSERT INTO cita_evento (id_cita, id_usuario_actor, tipo_evento, motivo, detalle)
SELECT
    c.id_cita,
    ur.id_usuario,
    'CANCELADA',
    c.motivo_cancelacion,
    'Cita demo cancelada por solicitud del paciente.'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
WHERE p.dni = '90000002'
  AND c.fecha = '2026-06-27'
  AND c.hora = '08:30:00'
  AND NOT EXISTS (
      SELECT 1
      FROM cita_evento ce
      WHERE ce.id_cita = c.id_cita
        AND ce.tipo_evento = 'CANCELADA'
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
    '2026-06-27',
    '10:00:00',
    'REPROGRAMADA',
    'Control ginecologico preventivo',
    TRUE,
    '2026-06-26 10:00:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'elena.villanueva'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000005'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-06-27'
        AND c.hora = '10:00:00'
  );

INSERT INTO cita (
    id_paciente,
    id_medico,
    id_recepcionista,
    id_cita_origen,
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
    origen.id_cita,
    '2026-06-28',
    '11:00:00',
    'CONFIRMADA',
    'Control ginecologico preventivo reprogramado',
    TRUE,
    '2026-06-27 12:30:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'elena.villanueva'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
INNER JOIN cita origen
    ON origen.id_paciente = p.id_paciente
    AND origen.id_medico = m.id_medico
    AND origen.fecha = '2026-06-27'
    AND origen.hora = '10:00:00'
WHERE p.dni = '90000005'
  AND NOT EXISTS (
      SELECT 1
      FROM cita c
      WHERE c.id_paciente = p.id_paciente
        AND c.id_medico = m.id_medico
        AND c.fecha = '2026-06-28'
        AND c.hora = '11:00:00'
  );

INSERT INTO cita_evento (
    id_cita,
    id_usuario_actor,
    id_cita_relacionada,
    tipo_evento,
    fecha_anterior,
    hora_anterior,
    fecha_nueva,
    hora_nueva,
    motivo,
    detalle
)
SELECT
    origen.id_cita,
    ur.id_usuario,
    nueva.id_cita,
    'REPROGRAMADA',
    origen.fecha,
    origen.hora,
    nueva.fecha,
    nueva.hora,
    'Paciente solicita nueva fecha',
    'Cita demo reprogramada con nueva cita confirmada.'
FROM cita origen
INNER JOIN paciente p ON p.id_paciente = origen.id_paciente
INNER JOIN usuario_sistema um ON um.username = 'elena.villanueva'
INNER JOIN medico m ON m.id_usuario = um.id_usuario AND m.id_medico = origen.id_medico
INNER JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
INNER JOIN cita nueva
    ON nueva.id_cita_origen = origen.id_cita
    AND nueva.fecha = '2026-06-28'
    AND nueva.hora = '11:00:00'
WHERE p.dni = '90000005'
  AND origen.fecha = '2026-06-27'
  AND origen.hora = '10:00:00'
  AND NOT EXISTS (
      SELECT 1
      FROM cita_evento ce
      WHERE ce.id_cita = origen.id_cita
        AND ce.tipo_evento = 'REPROGRAMADA'
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
    'Inasistencia a cita programada',
    'Se recomienda contactar al paciente para reprogramar si persiste la necesidad de atencion',
    'Registro demo de no asistencia sin evaluacion clinica presencial.',
    '2026-06-24 15:20:00'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '90000006'
  AND um.username = 'miguel.torres'
  AND c.fecha = '2026-06-24'
  AND c.hora = '15:00:00'
  AND c.estado = 'NO_ASISTIO'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-25', '08:00:00', '12:00:00', 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'luis.quispe'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-25', '09:00:00', '13:00:00', 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'ana.huaman'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-26', '08:00:00', '12:00:00', 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'carlos.choque'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO horario (id_medico, fecha, hora_inicio, hora_fin, estado)
SELECT m.id_medico, '2026-06-26', '14:00:00', '18:00:00', 'DISPONIBLE'
FROM medico m
INNER JOIN usuario_sistema u ON u.id_usuario = m.id_usuario
WHERE u.username = 'rosa.condori'
ON DUPLICATE KEY UPDATE estado = VALUES(estado);

INSERT INTO cita (id_paciente, id_medico, id_recepcionista, fecha, hora, estado, motivo_consulta, notificado, fecha_notificacion)
SELECT p.id_paciente, m.id_medico, r.id_recepcionista, '2026-06-25', '09:00:00', 'CONFIRMADA', 'Control de presión arterial', TRUE, '2026-06-24 16:20:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'luis.quispe'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000002'
  AND NOT EXISTS (SELECT 1 FROM cita c WHERE c.id_paciente = p.id_paciente AND c.id_medico = m.id_medico AND c.fecha = '2026-06-25' AND c.hora = '09:00:00');

INSERT INTO cita (id_paciente, id_medico, id_recepcionista, fecha, hora, estado, motivo_consulta, notificado, fecha_notificacion)
SELECT p.id_paciente, m.id_medico, r.id_recepcionista, '2026-06-25', '10:30:00', 'PENDIENTE', 'Dolor torácico leve para evaluación', FALSE, NULL
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'ana.huaman'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000005'
  AND NOT EXISTS (SELECT 1 FROM cita c WHERE c.id_paciente = p.id_paciente AND c.id_medico = m.id_medico AND c.fecha = '2026-06-25' AND c.hora = '10:30:00');

INSERT INTO cita (id_paciente, id_medico, id_recepcionista, fecha, hora, estado, motivo_consulta, notificado, fecha_notificacion)
SELECT p.id_paciente, m.id_medico, r.id_recepcionista, '2026-06-26', '09:30:00', 'CONFIRMADA', 'Control de crecimiento y vacunas', TRUE, '2026-06-25 08:10:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'carlos.choque'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000004'
  AND NOT EXISTS (SELECT 1 FROM cita c WHERE c.id_paciente = p.id_paciente AND c.id_medico = m.id_medico AND c.fecha = '2026-06-26' AND c.hora = '09:30:00');

INSERT INTO cita (id_paciente, id_medico, id_recepcionista, fecha, hora, estado, motivo_consulta, notificado, fecha_notificacion)
SELECT p.id_paciente, m.id_medico, r.id_recepcionista, '2026-06-24', '15:00:00', 'NO_ASISTIO', 'Revisión de lesión en rodilla', TRUE, '2026-06-23 12:40:00'
FROM paciente p
INNER JOIN usuario_sistema um ON um.username = 'miguel.torres'
INNER JOIN medico m ON m.id_usuario = um.id_usuario
LEFT JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
LEFT JOIN recepcionista r ON r.id_usuario = ur.id_usuario
WHERE p.dni = '90000006'
  AND NOT EXISTS (SELECT 1 FROM cita c WHERE c.id_paciente = p.id_paciente AND c.id_medico = m.id_medico AND c.fecha = '2026-06-24' AND c.hora = '15:00:00');

INSERT INTO cita_evento (id_cita, id_usuario_actor, tipo_evento, detalle)
SELECT c.id_cita, ur.id_usuario, 'NOTIFICADA', 'Recordatorio enviado al paciente.'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN usuario_sistema ur ON ur.username = 'valeria.nunez'
WHERE p.dni = '90000002'
  AND c.fecha = '2026-06-25'
  AND c.hora = '09:00:00'
  AND NOT EXISTS (SELECT 1 FROM cita_evento ce WHERE ce.id_cita = c.id_cita AND ce.tipo_evento = 'NOTIFICADA');

INSERT INTO cita_evento (id_cita, id_usuario_actor, tipo_evento, detalle)
SELECT c.id_cita, um.id_usuario, 'ATENDIDA', 'Atención médica registrada con historial.'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '90000001'
  AND c.fecha = '2026-05-20'
  AND c.hora = '09:00:00'
  AND NOT EXISTS (SELECT 1 FROM cita_evento ce WHERE ce.id_cita = c.id_cita AND ce.tipo_evento = 'ATENDIDA');

INSERT INTO cita_evento (id_cita, id_usuario_actor, tipo_evento, detalle)
SELECT c.id_cita, um.id_usuario, 'NO_ASISTIO', 'Paciente no se presentó a la cita programada.'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '90000006'
  AND c.fecha = '2026-06-24'
  AND c.hora = '15:00:00'
  AND NOT EXISTS (SELECT 1 FROM cita_evento ce WHERE ce.id_cita = c.id_cita AND ce.tipo_evento = 'NO_ASISTIO');

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
WHERE p.dni = '90000004'
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
WHERE p.dni = '90000003'
  AND um.username = 'rosa.condori'
  AND c.fecha = '2026-05-22'
  AND c.hora = '15:30:00'
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
    'Inasistencia a cita programada',
    'Se recomienda contactar al paciente para reprogramar si persiste la necesidad de atencion',
    'Registro demo de no asistencia sin evaluacion clinica presencial.',
    '2026-06-24 15:20:00'
FROM cita c
INNER JOIN paciente p ON p.id_paciente = c.id_paciente
INNER JOIN medico m ON m.id_medico = c.id_medico
INNER JOIN usuario_sistema um ON um.id_usuario = m.id_usuario
WHERE p.dni = '90000006'
  AND um.username = 'miguel.torres'
  AND c.fecha = '2026-06-24'
  AND c.hora = '15:00:00'
  AND c.estado = 'NO_ASISTIO'
  AND NOT EXISTS (
      SELECT 1
      FROM historial_cita hc
      WHERE hc.id_cita = c.id_cita
  );
