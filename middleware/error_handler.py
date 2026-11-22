"""
Manejo centralizado de errores para la API.
NUNCA expone el detalle interno de la excepción al cliente.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from utils.logger import logger


def register_error_handlers(app):

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.warning(f"INTEGRITY_ERROR method={request.method} path={request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Conflicto de datos: verifica llaves foráneas o valores únicos."},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        # Loguear internamente con el detalle completo, NUNCA enviarlo al cliente
        logger.error(
            f"INTERNAL_ERROR method={request.method} path={request.url.path} error={type(exc).__name__}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ocurrió un error interno. Por favor intenta más tarde."},
        )
