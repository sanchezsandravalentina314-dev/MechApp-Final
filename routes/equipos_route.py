"""
Rutas de Equipos.
- Listar/Obtener: público.
- Crear: usuario autenticado.
- Actualizar/Eliminar: solo Admin o capitán del equipo.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.equipos_schema import EquipoCreate, EquipoUpdate, EquipoResponse
from controllers import equipos_controller as controller
from utils.dependencies import get_current_user, require_role
from models.modelos import Usuario, Equipo, Rol

router = APIRouter(prefix="/api/equipos", tags=["Equipos"])


def _es_admin(usuario: Usuario, db: Session) -> bool:
    rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
    return rol and rol.nombre == "Administrador"


@router.get("/", response_model=List[EquipoResponse])
def listar_equipos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller.listar(db, skip, limit)


@router.get("/{item_id}", response_model=EquipoResponse)
def obtener_equipos(item_id: int, db: Session = Depends(get_db)):
    return controller.obtener(db, item_id)


@router.post("/", response_model=EquipoResponse, status_code=201)
def crear_equipos(
    datos: EquipoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=EquipoResponse)
def actualizar_equipos(
    item_id: int,
    datos: EquipoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    equipo = controller.obtener(db, item_id)
    if not _es_admin(usuario_actual, db) and equipo.id_capitan != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo el capitán o un administrador puede editar el equipo.")
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_equipos(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.eliminar(db, item_id)
