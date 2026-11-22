"""
Rutas de Notificaciones.
- Listar: Admin ve todas; usuario ve solo las suyas.
- Obtener/Actualizar/Eliminar: propietario o Admin.
- Crear: solo Admin (el sistema las genera).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.notificaciones_schema import NotificacionCreate, NotificacionUpdate, NotificacionResponse
from controllers import notificaciones_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Notificacion, Rol

router = APIRouter(prefix="/api/notificaciones", tags=["Notificaciones"])


def _es_admin(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre == "Administrador"


@router.get("/", response_model=List[NotificacionResponse])
def listar_notificaciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if _es_admin(usuario_actual, db):
        return controller.listar(db, skip, limit)
    return db.query(Notificacion).filter(
        Notificacion.id_usuario == usuario_actual.id_usuario
    ).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=NotificacionResponse)
def obtener_notificaciones(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    noti = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and noti.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permiso para ver esta notificación.")
    return noti


@router.post("/", response_model=NotificacionResponse, status_code=201)
def crear_notificaciones(
    datos: NotificacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=NotificacionResponse)
def actualizar_notificaciones(
    item_id: int,
    datos: NotificacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    noti = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and noti.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permiso para actualizar esta notificación.")
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_notificaciones(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.eliminar(db, item_id)
