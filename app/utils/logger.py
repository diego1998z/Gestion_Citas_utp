import logging


def get_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(nombre)


def log_error_tecnico(logger: logging.Logger, mensaje: str) -> None:
    """Registra detalle técnico internamente sin exponerlo al usuario."""
    logger.exception(mensaje)
