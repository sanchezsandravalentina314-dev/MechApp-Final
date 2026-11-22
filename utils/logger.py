"""
Logger estructurado centralizado para MechApp.
Registra eventos de seguridad críticos sin exponer datos sensibles.
"""
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("mechapp")
    if logger.handlers:
        return logger  # Ya configurado (evita duplicados en uvicorn --reload)

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", '
        '"module": "%(module)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Handler a stdout (capturado por Docker / systemd / uvicorn)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    logger.addHandler(stdout_handler)

    # Handler a archivo con rotación diaria (si existe carpeta logs/)
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        os.path.join(logs_dir, "mechapp.log"),
        when="midnight",
        backupCount=14,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


logger = _setup_logger()
