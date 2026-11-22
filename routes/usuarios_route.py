"""
Rutas de Usuarios.
- Listar/obtener: solo Admin o el propio usuario.
- Crear: público (registro alternativo vía admin).
- Actualizar/eliminar: solo Admin.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.usuarios_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from controllers import usuarios_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.listar(db, skip, limit)


@router.get("/{item_id}", response_model=UsuarioResponse)
def obtener_usuarios(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    # Un usuario solo puede ver su propio perfil; el Admin puede ver cualquiera
    from sqlalchemy.orm import Session as _S
    from models.modelos import Rol
    rol = db.query(Rol).filter(Rol.id_rol == usuario_actual.id_rol).first()
    if rol and rol.nombre == "Administrador":
        return controller.obtener(db, item_id)
    if usuario_actual.id_usuario != item_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver este perfil.")
    return controller.obtener(db, item_id)


@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuarios(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=UsuarioResponse)
def actualizar_usuarios(
    item_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    from models.modelos import Rol
    from fastapi import HTTPException, status
    rol = db.query(Rol).filter(Rol.id_rol == usuario_actual.id_rol).first()
    if not (rol and rol.nombre == "Administrador") and usuario_actual.id_usuario != item_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo puedes editar tu propio perfil.")
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_usuarios(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.eliminar(db, item_id)
