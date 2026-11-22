"""
Rutas de Reservas.
- Listar: solo Admin o Propietario (ven todas); Usuario ve solo las suyas.
- Obtener: usuario dueño de la reserva o Admin.
- Crear: cualquier usuario autenticado.
- Actualizar/Eliminar: dueño de la reserva o Admin.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.reservas_schema import ReservaCreate, ReservaUpdate, ReservaResponse
from controllers import reservas_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Reserva, Rol

router = APIRouter(prefix="/api/reservas", tags=["Reservas"])


def _es_admin_o_propietario(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre in ("Administrador", "Propietario")


@router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if _es_admin_o_propietario(usuario_actual, db):
        return controller.listar(db, skip, limit)
    # Usuario normal: solo sus propias reservas
    return db.query(Reserva).filter(
        Reserva.id_usuario == usuario_actual.id_usuario
    ).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ReservaResponse)
def obtener_reservas(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    reserva = controller.obtener(db, item_id)
    if not _es_admin_o_propietario(usuario_actual, db):
        if reserva.id_usuario != usuario_actual.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permiso para ver esta reserva.")
    return reserva


@router.post("/", response_model=ReservaResponse, status_code=201)
def crear_reservas(
    datos: ReservaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=ReservaResponse)
def actualizar_reservas(
    item_id: int,
    datos: ReservaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    reserva = controller.obtener(db, item_id)
    if not _es_admin_o_propietario(usuario_actual, db):
        if reserva.id_usuario != usuario_actual.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permiso para modificar esta reserva.")
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_reservas(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    reserva = controller.obtener(db, item_id)
    if not _es_admin_o_propietario(usuario_actual, db):
        if reserva.id_usuario != usuario_actual.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permiso para eliminar esta reserva.")
    return controller.eliminar(db, item_id)
