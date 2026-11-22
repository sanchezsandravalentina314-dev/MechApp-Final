"""
Punto de entrada de la API de MechApp.
Ejecutar desde App/Backend con:
    uvicorn main:app --reload
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

import os

from config.settings import settings
from config.database import init_db
from middleware.error_handler import register_error_handlers
from utils.rate_limiter import limiter

from routes import (
    auth_route,
    roles_route,
    usuarios_route,
    ubicaciones_route,
    canchas_route,
    horarios_route,
    reservas_route,
    torneos_route,
    inscripciones_route,
    equipos_route,
    equipo_jugador_route,
    inscripcion_equipos_route,
    partidas_route,
    resultados_route,
    metodos_pago_route,
    pagos_route,
    notificaciones_route,
    valoraciones_route,
    favoritos_route,
    propietarios_route,
    eventos_route,
    noticias_route,
    reportes_route,
    consumo_route,
)

# ── Crear la aplicación ────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="API para la digitalización de la gestión del tejo (Turmequé).",
    version="2.0.0",
    # Docs solo en desarrollo (DEBUG=True), deshabilitados en producción
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# ── Rate Limiter ────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -- CORS -------------------------------------------------------------------
_DEFAULT_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5174,http://127.0.0.1:5174,"
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:8081,http://127.0.0.1:8081,"
    "http://localhost:8082,http://127.0.0.1:8082"
)
origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Manejadores de error ───────────────────────────────────────────────────
register_error_handlers(app)

# ── Registrar routers ──────────────────────────────────────────────────────
for module in (
    auth_route, roles_route, usuarios_route, ubicaciones_route, canchas_route,
    horarios_route, reservas_route, torneos_route, inscripciones_route,
    equipos_route, equipo_jugador_route, inscripcion_equipos_route,
    partidas_route, resultados_route, metodos_pago_route, pagos_route,
    notificaciones_route, valoraciones_route, favoritos_route,
    propietarios_route, eventos_route, noticias_route, reportes_route,
    consumo_route,
):
    app.include_router(module.router)

# ── Eventos del ciclo de vida ──────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()

# ── Endpoints básicos ──────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {"mensaje": "MechApp API funcionando correctamente"}

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
