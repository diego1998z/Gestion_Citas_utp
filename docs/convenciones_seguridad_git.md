# Guía de convenciones, seguridad y Git

## Clean Code y convenciones

- Clases: PascalCase (`PacienteModel`).
- Funciones, variables y archivos Python: `snake_case` (`validar_paciente_form`).
- Constantes: `UPPER_SNAKE_CASE`.
- Nombres descriptivos y específicos.
- Una responsabilidad por función.
- Templates sin SQL ni conexiones a base de datos.
- Modelos con SQL parametrizado.
- Controladores para validación, autorización y coordinación del flujo.

## Seguridad

- No concatenar valores de usuario en SQL.
- Validar todos los formularios en servidor.
- Usar hash para contraseñas; nunca texto plano.
- Proteger rutas por rol.
- Proteger formularios POST con CSRF.
- Definir `SECRET_KEY` segura en producción.
- No versionar `.env`, API keys de Brevo, credenciales SMTP ni logs.
- Mostrar mensajes amigables y registrar detalle técnico en logs. Los errores de correo deben registrarse sin exponer API keys ni contraseñas.

## Manejo de errores y logs

- Usar transacciones con rollback ante fallos de base de datos.
- Capturar errores esperables y convertirlos en mensajes claros.
- Registrar errores técnicos con `app.logger.exception` o `app.logger.error(..., exc_info=True)`.
- No mostrar trazas ni mensajes SQL al usuario final.

## Git

- Usar commits convencionales:
  - `feat: ...`
  - `fix: ...`
  - `docs: ...`
  - `refactor: ...`
- No agregar `Co-Authored-By` ni atribuciones automáticas.
- Revisar `git status` antes de commitear.
- No commitear `.env`, `logs/`, `__pycache__/` ni entornos virtuales.

- Para futuras versiones colaborativas, se recomienda trabajar con Pull Requests y Code Review antes de integrar cambios a `master`/`main`. Este punto queda como mejora del flujo, no como práctica obligatoria aplicada durante el desarrollo actual.
