# Sistema de Gestión de Citas Médicas

MVP Flask + MySQL/InnoDB para la Clínica Universitaria de Comas.

## Estado actual

Batch B deja implementada la seguridad transversal inicial:

- estructura MVC,
- app factory de Flask,
- configuración MySQL por variables de entorno,
- helpers de conexión/transacción,
- templates base sin SQL,
- schema inicial de base de datos,
- login/logout con sesión Flask,
- verificación de contraseña con Werkzeug,
- decoradores `login_required` y `roles_required`,
- errores amigables y logging interno en `logs/app.log`.

Los CRUDs y flujos de citas se implementan en batches posteriores.

## Configuración mínima

1. Copiar `.env.example` a `.env`.
2. Ajustar credenciales MySQL.
3. Crear la base ejecutando `database/schema.sql`.
4. Opcional: cargar `database/seed.sql`.

## Usuario demo

Si cargás `database/seed.sql`, queda disponible:

- Usuario: `admin`
- Contraseña: `Admin123*`
- Rol: `ADMINISTRADOR`

No ejecutar build: este proyecto es Flask server-rendered y la guía del proyecto indica no hacer build después de cambios.
