"""
Rutas de Valoraciones.
- Listar/Obtener: público.
- Crear: usuario autenticado (una por cancha por usuario, controlado por DB unique).
- Actualizar/Eliminar: propietario de la valoración o Admin.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.valoraciones_schema import ValoracionCreate, ValoracionUpdate, ValoracionResponse
from controllers import valoraciones_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Valoracion, Rol

router = APIRouter(prefix="/api/valoraciones", tags=["Valoraciones"])


def _es_admin(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre == "Administrador"


@router.get("/", response_model=List[ValoracionResponse])
def listar_valoraciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller.listar(db, skip, limit)


@router.get("/{item_id}", response_model=ValoracionResponse)
def obtener_valoraciones(item_id: int, db: Session = Depends(get_db)):
    return controller.obtener(db, item_id)


@router.post("/", response_model=ValoracionResponse, status_code=201)
def crear_valoraciones(
    datos: ValoracionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=ValoracionResponse)
def actualizar_valoraciones(
    item_id: int,
    datos: ValoracionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    valoracion = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and valoracion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo puedes editar tus propias valoraciones.")
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_valoraciones(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    valoracion = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and valoracion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo puedes eliminar tus propias valoraciones.")
    return controller.eliminar(db, item_id)
