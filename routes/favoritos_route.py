"""
Rutas de Favoritos.
- Listar: usuario ve solo los suyos; Admin ve todos.
- Obtener/Eliminar: propietario del favorito o Admin.
- Crear: usuario autenticado.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.favoritos_schema import FavoritoCreate, FavoritoUpdate, FavoritoResponse
from controllers import favoritos_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Favorito, Rol

router = APIRouter(prefix="/api/favoritos", tags=["Favoritos"])


def _es_admin(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre == "Administrador"


@router.get("/", response_model=List[FavoritoResponse])
def listar_favoritos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if _es_admin(usuario_actual, db):
        return controller.listar(db, skip, limit)
    return db.query(Favorito).filter(
        Favorito.id_usuario == usuario_actual.id_usuario
    ).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=FavoritoResponse)
def obtener_favoritos(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    fav = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and fav.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permiso para ver este favorito.")
    return fav


@router.post("/", response_model=FavoritoResponse, status_code=201)
def crear_favoritos(
    datos: FavoritoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=FavoritoResponse)
def actualizar_favoritos(
    item_id: int,
    datos: FavoritoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_favoritos(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    fav = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and fav.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo puedes eliminar tus propios favoritos.")
    return controller.eliminar(db, item_id)
