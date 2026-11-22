"""
Configuración general de la aplicación (variables de entorno).
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _require(var: str) -> str:
    """Lee una variable de entorno obligatoria; aborta si no está definida."""
    value = os.getenv(var)
    if not value:
        print(f"[CONFIG] ERROR: La variable de entorno '{var}' es obligatoria y no está definida.", file=sys.stderr)
        sys.exit(1)
    return value


class Settings:
    APP_NAME: str = "MechApp API"

    # En producción debe ser False. Por defecto False para seguridad.
    DEBUG: bool = os.getenv("DEBUG", "False").strip().lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:1983@localhost:5433/MechApp"
    )

    # SECRET_KEY es obligatoria; sin ella la app no arranca
    SECRET_KEY: str = _require("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
