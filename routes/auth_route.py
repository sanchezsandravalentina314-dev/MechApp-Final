from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.auth_schema import UsuarioRegistro, UsuarioLogin, Token, SolicitudRecuperacion, RestablecerContrasena
from controllers import auth_controllers
from utils.rate_limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/registro", response_model=Token, status_code=201)
@limiter.limit("5/minute")
def registro(request: Request, datos: UsuarioRegistro, db: Session = Depends(get_db)):
    return auth_controllers.registrar_usuario(db, datos)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, datos: UsuarioLogin, db: Session = Depends(get_db)):
    return auth_controllers.login_usuario(db, datos)


@router.post("/recuperar-contrasena")
@limiter.limit("3/minute")
def recuperar_contrasena(request: Request, datos: SolicitudRecuperacion, db: Session = Depends(get_db)):
    return auth_controllers.solicitar_recuperacion(db, datos)


@router.post("/restablecer-contrasena")
@limiter.limit("5/minute")
def restablecer_contrasena(request: Request, datos: RestablecerContrasena, db: Session = Depends(get_db)):
    return auth_controllers.restablecer_contrasena(db, datos)
