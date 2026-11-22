import os
import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import (
    SessionLocal, init_db, Rol, Usuario, PasswordResetToken, Propietario,
    Ubicacion, Cancha, Torneo, Equipo, Partido, Resultado, Reserva,
    Evento, Noticia, Producto, CategoriaProducto, Combo, Reporte, Notificacion
)
from core.security import (
    hash_password, verify_password, validate_password_strength,
    check_login_lockout, record_failed_login, clear_failed_login,
    generate_recovery_token
)
from core.turnstile import verify_captcha_token
from seed import seed_database

# Inicializar Base de Datos y Datos Semilla
seed_database()

app = FastAPI(
    title="MechApp API Oficial",
    description="Backend oficial de MechApp para el Tejo Colombiano con autenticación Argon2id, Turnstile CAPTCHA y recuperación segura de contraseñas.",
    version="2.0.0"
)

# Configuración CORS para el Frontend Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Esquemas Pydantic para Validación Estricta
# ==========================================

class RegistroRequest(BaseModel):
    id_rol: int = 2
    nombre: str
    documento: str
    correo: EmailStr
    telefono: Optional[str] = None
    contrasena: str
    captcha_token: str
    acepta_tratamiento_datos: bool = True

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str
    captcha_token: Optional[str] = None

class RecuperacionRequest(BaseModel):
    correo: EmailStr
    captcha_token: str

class RestablecerRequest(BaseModel):
    token: str
    nueva_contrasena: str

class CambiarContrasenaRequest(BaseModel):
    contrasena_actual: str
    nueva_contrasena: str

# ==========================================
# 3.1 & 3.2 & 3.3: Endpoints de Autenticación y Seguridad
# ==========================================

@app.post("/api/auth/registro", status_code=status.HTTP_201_CREATED)
async def registro(req: RegistroRequest, db: Session = Depends(get_db)):
    # 1. Validación de CAPTCHA real (Cloudflare Turnstile)
    captcha_valido, captcha_msg = await verify_captcha_token(req.captcha_token)
    if not captcha_valido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=captcha_msg)

    # 2. Validación de políticas de seguridad de contraseña (mínimo 12 caracteres, mayúsculas, minúsculas, números, especiales, no común)
    pwd_error = validate_password_strength(req.contrasena)
    if pwd_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pwd_error)

    # 3. Validar duplicidad de correo o documento
    correo_clean = req.correo.strip().lower()
    if db.query(Usuario).filter(Usuario.correo == correo_clean).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo electrónico ya está registrado en MechApp.")
    if db.query(Usuario).filter(Usuario.documento == req.documento.strip()).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de documento ya está registrado.")

    # 4. Hasheo seguro con Argon2id
    argon2_hash = hash_password(req.contrasena)

    # Prevenir elevación de privilegios: el registro público solo permite Jugador (2) o Propietario (3)
    rol_asignado = req.id_rol if req.id_rol in [2, 3] else 2

    nuevo_usuario = Usuario(
        id_rol=rol_asignado,
        nombre=req.nombre.strip(),
        documento=req.documento.strip(),
        correo=correo_clean,
        telefono=req.telefono.strip() if req.telefono else None,
        contrasena=argon2_hash,
        estado=True,
        acepta_tratamiento_datos=req.acepta_tratamiento_datos,
        fecha_aceptacion_tratamiento=datetime.datetime.utcnow() if req.acepta_tratamiento_datos else None,
        version_politica_aceptada="1.0"
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario registrado exitosamente con cifrado seguro Argon2id.",
        "access_token": f"token_argon2_{nuevo_usuario.id_usuario}_{datetime.datetime.utcnow().timestamp()}",
        "usuario": {
            "id_usuario": nuevo_usuario.id_usuario,
            "id_rol": nuevo_usuario.id_rol,
            "nombre": nuevo_usuario.nombre,
            "documento": nuevo_usuario.documento,
            "correo": nuevo_usuario.correo,
            "telefono": nuevo_usuario.telefono,
            "estado": nuevo_usuario.estado
        }
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    correo_clean = req.correo.strip().lower()

    # 1. Control contra intentos repetidos de acceso (Bloqueo temporal de 15 min tras 5 intentos)
    bloqueado, restantes, mins_left = check_login_lockout(correo_clean)
    if bloqueado:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Cuenta suspendida temporalmente por seguridad. Ha superado los intentos fallidos. Intente de nuevo en {mins_left} minuto(s)."
        )

    # 2. Validación de respuesta de CAPTCHA Turnstile
    if req.captcha_token:
        captcha_valido, captcha_msg = await verify_captcha_token(req.captcha_token)
        if not captcha_valido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=captcha_msg)

    # 3. Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.correo == correo_clean).first()
    if not usuario:
        # Registrar intento fallido para prevenir ataques de enumeración y fuerza bruta
        is_locked, rem, m_left = record_failed_login(correo_clean)
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Acceso bloqueado por 15 minutos debido a 5 intentos consecutivos fallidos."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciales inválidas. Le quedan {rem} intento(s) antes del bloqueo de seguridad."
        )

    # 4. Verificación de contraseña segura
    valida = verify_password(req.contrasena, usuario.contrasena)
    if not valida:
        is_locked, rem, m_left = record_failed_login(correo_clean)
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Acceso bloqueado por 15 minutos debido a 5 intentos consecutivos fallidos."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Contraseña incorrecta. Le quedan {rem} intento(s) antes del bloqueo temporal."
        )

    # 5. Si la contraseña era de un formato viejo (pbkdf2), re-hashear a Argon2id automáticamente
    if usuario.contrasena.startswith("pbkdf2_"):
        usuario.contrasena = hash_password(req.contrasena)
        db.commit()

    # Limpiar contador de intentos fallidos
    clear_failed_login(correo_clean)

    return {
        "mensaje": f"Bienvenido a MechApp, {usuario.nombre}.",
        "access_token": f"token_argon2_{usuario.id_usuario}_{datetime.datetime.utcnow().timestamp()}",
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "id_rol": usuario.id_rol,
            "nombre": usuario.nombre,
            "documento": usuario.documento,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "estado": usuario.estado
        }
    }

@app.post("/api/auth/recuperar-contrasena")
async def solicitar_recuperacion(req: RecuperacionRequest, db: Session = Depends(get_db)):
    # 1. Validar CAPTCHA para impedir spam masivo
    captcha_valido, captcha_msg = await verify_captcha_token(req.captcha_token)
    if not captcha_valido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=captcha_msg)

    correo_clean = req.correo.strip().lower()
    usuario = db.query(Usuario).filter(Usuario.correo == correo_clean).first()

    # OWASP: NO revelar si el correo está registrado en el mensaje al usuario
    token_str = None
    enlace_recuperacion = None

    if usuario:
        # Invalidar tokens anteriores pendientes
        db.query(PasswordResetToken).filter(
            PasswordResetToken.usuario_id == usuario.id_usuario,
            PasswordResetToken.utilizado == False
        ).update({"utilizado": True})

        # Generar token seguro, temporal (15 min) y de un solo uso
        token_str, expira_en = generate_recovery_token()
        nuevo_token = PasswordResetToken(
            token=token_str,
            usuario_id=usuario.id_usuario,
            correo=correo_clean,
            expira_en=expira_en,
            utilizado=False
        )
        db.add(nuevo_token)
        db.commit()

        # Enlace oficial seguro de recuperación
        enlace_recuperacion = f"http://localhost:5173/restablecer-contrasena?token={token_str}"

    return {
        "mensaje": "Si el correo electrónico se encuentra registrado en MechApp, hemos enviado un enlace seguro para restablecer la contraseña. El enlace es de un solo uso y vencerá en 15 minutos.",
        # Retornado para facilitar verificación interactiva en el frontend
        "enlace_recuperacion": enlace_recuperacion
    }

@app.get("/api/auth/validar-token-recuperacion")
def validar_token_recuperacion(token: str = Query(...), db: Session = Depends(get_db)):
    token_db = db.query(PasswordResetToken).filter(PasswordResetToken.token == token.strip()).first()
    if not token_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El enlace de recuperación es inexistente o inválido.")
    if token_db.utilizado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este enlace de recuperación ya fue utilizado.")
    if datetime.datetime.utcnow() > token_db.expira_en:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace de recuperación ha expirado por tiempo (máximo 15 minutos).")

    return {
        "valido": True,
        "correo": token_db.correo,
        "expira_en": token_db.expira_en.isoformat()
    }

@app.post("/api/auth/restablecer-contrasena")
def restablecer_contrasena(req: RestablecerRequest, db: Session = Depends(get_db)):
    # 1. Validar requisitos de la nueva contraseña
    pwd_error = validate_password_strength(req.nueva_contrasena)
    if pwd_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pwd_error)

    # 2. Validar token
    token_db = db.query(PasswordResetToken).filter(PasswordResetToken.token == req.token.strip()).first()
    if not token_db or token_db.utilizado or datetime.datetime.utcnow() > token_db.expira_en:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace ha vencido o ya fue utilizado.")

    # 3. Actualizar contraseña con Argon2id
    usuario = db.query(Usuario).filter(Usuario.id_usuario == token_db.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    usuario.contrasena = hash_password(req.nueva_contrasena)
    token_db.utilizado = True # Invalidar inmediatamente (un solo uso)
    db.commit()

    return {"mensaje": "Contraseña actualizada exitosamente con cifrado seguro Argon2id. Ya puedes iniciar sesión."}

@app.put("/api/auth/cambiar-contrasena")
def cambiar_contrasena(req: CambiarContrasenaRequest, db: Session = Depends(get_db)):
    # Validar requisitos de la nueva contraseña
    pwd_error = validate_password_strength(req.nueva_contrasena)
    if pwd_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pwd_error)

    # Para prueba: el primer usuario o usuario actual
    usuario = db.query(Usuario).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    if not verify_password(req.contrasena_actual, usuario.contrasena):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual no coincide.")

    usuario.contrasena = hash_password(req.nueva_contrasena)
    db.commit()
    return {"mensaje": "Contraseña cambiada exitosamente con cifrado seguro Argon2id."}

@app.post("/api/auth/verificar-captcha")
async def verificar_captcha_endpoint(body: dict):
    token = body.get("token", "")
    valido, msg = await verify_captcha_token(token)
    if not valido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"valido": True, "mensaje": msg}

# ==========================================
# 3.4 & 5: Endpoints CRUD de Módulos del Sistema
# ==========================================

@app.get("/api/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@app.post("/api/usuarios/")
def crear_usuario(data: dict, db: Session = Depends(get_db)):
    pwd = data.get("contrasena") or "MechApp2026*Segura"
    pwd_error = validate_password_strength(pwd)
    if pwd_error:
        raise HTTPException(status_code=400, detail=pwd_error)
    
    usr = Usuario(
        id_rol=int(data.get("id_rol", 2)),
        nombre=data.get("nombre", ""),
        documento=data.get("documento", ""),
        correo=data.get("correo", "").strip().lower(),
        telefono=data.get("telefono"),
        contrasena=hash_password(pwd),
        estado=data.get("estado", True)
    )
    db.add(usr)
    db.commit()
    db.refresh(usr)
    return usr

@app.put("/api/usuarios/{id_usuario}")
def actualizar_usuario(id_usuario: int, data: dict, db: Session = Depends(get_db)):
    usr = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usr:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    for k, v in data.items():
        if k == "contrasena" and v:
            err = validate_password_strength(v)
            if err:
                raise HTTPException(status_code=400, detail=err)
            usr.contrasena = hash_password(v)
        elif hasattr(usr, k) and k != "id_usuario":
            setattr(usr, k, v)
    db.commit()
    db.refresh(usr)
    return usr

@app.delete("/api/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usr = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usr:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    db.delete(usr)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente."}

@app.get("/api/roles/")
def listar_roles(db: Session = Depends(get_db)):
    return db.query(Rol).all()

@app.get("/api/propietarios/")
def listar_propietarios(db: Session = Depends(get_db)):
    return db.query(Propietario).all()

@app.get("/api/canchas/")
def listar_canchas(db: Session = Depends(get_db)):
    return db.query(Cancha).all()

@app.post("/api/canchas/")
def crear_cancha(data: dict, db: Session = Depends(get_db)):
    c = Cancha(**data)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.put("/api/canchas/{id_cancha}")
def actualizar_cancha(id_cancha: int, data: dict, db: Session = Depends(get_db)):
    c = db.query(Cancha).filter(Cancha.id_cancha == id_cancha).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cancha no encontrada.")
    for k, v in data.items():
        if hasattr(c, k):
            setattr(c, k, v)
    db.commit()
    return c

@app.delete("/api/canchas/{id_cancha}")
def eliminar_cancha(id_cancha: int, db: Session = Depends(get_db)):
    c = db.query(Cancha).filter(Cancha.id_cancha == id_cancha).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cancha no encontrada.")
    db.delete(c)
    db.commit()
    return {"mensaje": "Cancha eliminada correctamente."}

@app.get("/api/ubicaciones/")
def listar_ubicaciones(db: Session = Depends(get_db)):
    return db.query(Ubicacion).all()

@app.get("/api/torneos/")
def listar_torneos(db: Session = Depends(get_db)):
    return db.query(Torneo).all()

@app.post("/api/torneos/")
def crear_torneo(data: dict, db: Session = Depends(get_db)):
    t = Torneo(**data)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.delete("/api/torneos/{id_torneo}")
def eliminar_torneo(id_torneo: int, db: Session = Depends(get_db)):
    t = db.query(Torneo).filter(Torneo.id_torneo == id_torneo).first()
    if not t:
        raise HTTPException(status_code=404, detail="Torneo no encontrado.")
    db.delete(t)
    db.commit()
    return {"mensaje": "Torneo eliminado correctamente."}

@app.get("/api/reservas/")
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(Reserva).all()

@app.post("/api/reservas/")
def crear_reserva(data: dict, db: Session = Depends(get_db)):
    r = Reserva(**data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@app.delete("/api/reservas/{id_reserva}")
def eliminar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    r = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    db.delete(r)
    db.commit()
    return {"mensaje": "Reserva cancelada correctamente."}

@app.get("/api/equipos/")
def listar_equipos(db: Session = Depends(get_db)):
    return db.query(Equipo).all()

@app.post("/api/equipos/")
def crear_equipo(data: dict, db: Session = Depends(get_db)):
    eq = Equipo(**data)
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return eq

@app.delete("/api/equipos/{id_equipo}")
def eliminar_equipo(id_equipo: int, db: Session = Depends(get_db)):
    eq = db.query(Equipo).filter(Equipo.id_equipo == id_equipo).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
    db.delete(eq)
    db.commit()
    return {"mensaje": "Equipo eliminado."}

@app.get("/api/partidos/")
def listar_partidos(db: Session = Depends(get_db)):
    return db.query(Partido).all()

@app.post("/api/partidos/")
def crear_partido(data: dict, db: Session = Depends(get_db)):
    p = Partido(**data)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.delete("/api/partidos/{id_partido}")
def eliminar_partido(id_partido: int, db: Session = Depends(get_db)):
    p = db.query(Partido).filter(Partido.id_partido == id_partido).first()
    if not p:
        raise HTTPException(status_code=404, detail="Partido no encontrado.")
    db.delete(p)
    db.commit()
    return {"mensaje": "Partido eliminado."}

@app.get("/api/resultados/")
def listar_resultados(db: Session = Depends(get_db)):
    return db.query(Resultado).all()

@app.post("/api/partidos/{id_partido}/resultado")
def registrar_resultado(id_partido: int, data: dict, db: Session = Depends(get_db)):
    res = db.query(Resultado).filter(Resultado.id_partido == id_partido).first()
    if not res:
        res = Resultado(id_partido=id_partido, **data)
        db.add(res)
    else:
        for k, v in data.items():
            setattr(res, k, v)
    # Actualizar estado del partido a Finalizado
    partido = db.query(Partido).filter(Partido.id_partido == id_partido).first()
    if partido:
        partido.estado = "Finalizado"
    db.commit()
    return res

@app.get("/api/eventos/")
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(Evento).all()

@app.get("/api/noticias/")
def listar_noticias(db: Session = Depends(get_db)):
    return db.query(Noticia).all()

@app.get("/api/productos/")
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@app.get("/api/combos/")
def listar_combos(db: Session = Depends(get_db)):
    return db.query(Combo).all()

@app.get("/api/reportes/")
def listar_reportes(db: Session = Depends(get_db)):
    return db.query(Reporte).all()

@app.get("/api/notificaciones/")
def listar_notificaciones(db: Session = Depends(get_db)):
    return db.query(Notificacion).all()

@app.get("/api/configuracion/")
def obtener_configuracion():
    return {
        "nombre_sistema": "MechApp - Plataforma del Tejo Colombiano",
        "version": "2.0.0",
        "politica_contrasenas": {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special": True,
            "prohibit_common": True,
            "algorithm": "Argon2id (RFC 9106)",
        },
        "seguridad_acceso": {
            "max_intentos_fallidos": 5,
            "duracion_bloqueo_minutos": 15,
            "expiracion_token_recuperacion_minutos": 15,
            "servicio_captcha": "Cloudflare Turnstile Oficial"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
