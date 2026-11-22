import re
import secrets
import datetime
from typing import Optional, Dict, Tuple
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import jwt

# ==========================================
# 1. Algoritmo Criptográfico Seguro: Argon2id
# ==========================================
# Configuración recomendada por OWASP para Argon2id:
# - Type: Type.ID (Argon2id es resistente a ataques de canal lateral y GPU/ASIC)
# - Time cost: 2 iteraciones
# - Memory cost: 65536 KiB (64 MB)
# - Parallelism: 1 hilo
# - Hash length: 32 bytes
argon2_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    type=Type.ID
)

# Diccionario de contraseñas comunes y vulnerables que deben ser rechazadas
COMMON_PASSWORDS = {
    'password', 'password123', 'password1234', '123456789012', '1234567890123',
    'admin123456', 'admin1234567', 'mechapp1234', 'mechapp2024!', 'mechapp2025!',
    'mechapp2026!', 'qwertyuiop12', 'colombia1234', 'tejo12345678', 'contrasena12',
    'contrasena123', 'password12345', 'supersecret1', 'iloveyou1234', 'welcome12345',
    '111111111111', '000000000000', '123123123123', 'abc123abc123'
}

def hash_password(password: str) -> str:
    """
    Almacena contraseñas mediante algoritmo seguro Argon2id.
    Nunca almacena en texto plano.
    """
    return argon2_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña en texto plano contra el hash almacenado.
    Soporta Argon2id y compatibilidad con pbkdf2 legado de migraciones.
    """
    if not hashed_password or not plain_password:
        return False
    
    # Si fue hasheada con Argon2id
    if hashed_password.startswith("$argon2"):
        try:
            return argon2_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, InvalidHashError):
            return False
            
    # Compatibilidad con hashes existentes en backup (pbkdf2_sha256)
    if hashed_password.startswith("pbkdf2_sha256$"):
        import hashlib
        try:
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt = parts[1]
                stored_hash = parts[2]
                computed = hashlib.pbkdf2_hmac(
                    'sha256',
                    plain_password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                ).hex()
                return secrets.compare_digest(stored_hash, computed)
        except Exception:
            return False

    return False

def validate_password_strength(password: str) -> Optional[str]:
    """
    Valida las reglas estrictas de seguridad de contraseña:
    - Mínimo 12 caracteres.
    - Letras mayúsculas, minúsculas, números y caracteres especiales.
    - Evitar contraseñas comunes o comprometidas.
    Retorna None si cumple, o el mensaje de error explicativo.
    """
    if not password or len(password) < 12:
        return "La contraseña debe tener un mínimo de 12 caracteres."
    if not re.search(r'[A-Z]', password):
        return "La contraseña debe contener al menos una letra mayúscula (A-Z)."
    if not re.search(r'[a-z]', password):
        return "La contraseña debe contener al menos una letra minúscula (a-z)."
    if not re.search(r'[0-9]', password):
        return "La contraseña debe contener al menos un número (0-9)."
    if not re.search(r'[^A-Za-z0-9]', password):
        return "La contraseña debe contener al menos un carácter especial (!@#$%^&*...)."
    
    pwd_lower = password.lower()
    for common in COMMON_PASSWORDS:
        if common in pwd_lower:
            return f"La contraseña es demasiado predecible o contiene términos comunes ('{common}'). Elija una más segura."

    return None

# ==========================================
# 2. Control contra Intentos Repetidos (Lockout)
# ==========================================
_failed_attempts: Dict[str, Dict] = {}

def check_login_lockout(email: str) -> Tuple[bool, int, int]:
    """
    Verifica si una cuenta o IP está bloqueada por intentos fallidos.
    Retorna: (esta_bloqueada, intentos_restantes, minutos_restantes)
    """
    key = email.strip().lower()
    record = _failed_attempts.get(key)
    now = datetime.datetime.utcnow()

    if not record:
        return (False, 5, 0)

    # Si hay bloqueo activo de 15 minutos
    if record.get("locked_until"):
        if now < record["locked_until"]:
            mins_left = max(1, int((record["locked_until"] - now).total_seconds() // 60))
            return (True, 0, mins_left)
        else:
            # Expiró el bloqueo: reiniciar contador
            del _failed_attempts[key]
            return (False, 5, 0)

    attempts = record.get("count", 0)
    remaining = max(0, 5 - attempts)
    return (False, remaining, 0)

def record_failed_login(email: str) -> Tuple[bool, int, int]:
    """
    Registra un intento de login fallido. Bloquea por 15 minutos tras 5 intentos.
    """
    key = email.strip().lower()
    now = datetime.datetime.utcnow()
    record = _failed_attempts.setdefault(key, {"count": 0, "last_attempt": now, "locked_until": None})

    record["count"] += 1
    record["last_attempt"] = now

    if record["count"] >= 5:
        record["locked_until"] = now + datetime.timedelta(minutes=15)
        return (True, 0, 15)

    remaining = max(0, 5 - record["count"])
    return (False, remaining, 0)

def clear_failed_login(email: str) -> None:
    """Limpia el registro de intentos tras un acceso exitoso."""
    key = email.strip().lower()
    if key in _failed_attempts:
        del _failed_attempts[key]

# ==========================================
# 3. Tokens Criptográficos Seguros y Temporales
# ==========================================
def generate_recovery_token() -> Tuple[str, datetime.datetime]:
    """
    Genera un token de 64 caracteres criptográficamente seguro,
    temporal (vence en 15 minutos) y de un solo uso.
    """
    token = secrets.token_hex(32) # 64 caracteres hex
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    return (token, expires_at)
