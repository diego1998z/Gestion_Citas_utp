import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

from app.utils.auth import get_current_user
from config.settings import Config


csrf = CSRFProtect()


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="views",
        static_folder="static",
    )
    app.config.from_object(config_class)

    csrf.init_app(app)

    configure_logging(app)
    register_blueprints(app)
    register_template_context(app)
    register_error_handlers(app)

    return app


def configure_logging(app: Flask) -> None:
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)

    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    file_handler = RotatingFileHandler(
        logs_path / "app.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    app.logger.setLevel(log_level)
    if not any(isinstance(handler, RotatingFileHandler) for handler in app.logger.handlers):
        app.logger.addHandler(file_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if not any(isinstance(handler, RotatingFileHandler) for handler in root_logger.handlers):
        root_logger.addHandler(file_handler)


def register_blueprints(app: Flask) -> None:
    from app.controllers.auth_controller import auth_bp
    from app.controllers.cita_controller import citas_bp
    from app.controllers.historial_controller import historial_bp
    from app.controllers.home_controller import home_bp
    from app.controllers.medico_controller import medicos_bp
    from app.controllers.paciente_controller import pacientes_bp
    from app.controllers.reporte_controller import reportes_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pacientes_bp)
    app.register_blueprint(medicos_bp)
    app.register_blueprint(citas_bp)
    app.register_blueprint(historial_bp)
    app.register_blueprint(reportes_bp)


def register_template_context(app: Flask) -> None:
    @app.context_processor
    def inject_current_user() -> dict:
        return {"current_user": get_current_user()}


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        app.logger.warning("Solicitud POST bloqueada por CSRF: %s", error.description)
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error("Error interno no controlado", exc_info=True)
        return render_template("errors/500.html"), 500
