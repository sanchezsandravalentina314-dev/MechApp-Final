"""
Rutas de Inscripciones.
- Listar: Admin ve todas; usuario ve solo las suyas.
- Obtener: propietario de la inscripción o Admin.
- Crear: usuario autenticado.
- Actualizar/Eliminar: solo Admin.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.inscripciones_schema import InscripcionCreate, InscripcionUpdate, InscripcionResponse
from controllers import inscripciones_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Inscripcion, Rol

router = APIRouter(prefix="/api/inscripciones", tags=["Inscripciones"])


def _es_admin(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre == "Administrador"


@router.get("/", response_model=List[InscripcionResponse])
def listar_inscripciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if _es_admin(usuario_actual, db):
        return controller.listar(db, skip, limit)
    return db.query(Inscripcion).filter(
        Inscripcion.id_usuario == usuario_actual.id_usuario
    ).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=InscripcionResponse)
def obtener_inscripciones(
    item_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    inscripcion = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and inscripcion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permiso para ver esta inscripción.")
    return inscripcion


@router.post("/", response_model=InscripcionResponse, status_code=201)
def crear_inscripciones(
    datos: InscripcionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=InscripcionResponse)
def actualizar_inscripciones(
    item_id: int,
    datos: InscripcionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_inscripciones(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.eliminar(db, item_id)
