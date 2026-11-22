"""
Rutas de Eventos.
- Listar/Obtener: público.
- Crear/Actualizar/Eliminar: solo Admin o Propietario.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from schemas.eventos_schema import EventoCreate, EventoUpdate, EventoResponse
from controllers import eventos_controller as controller
from utils.dependencies import require_role
from models.modelos import Usuario

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])


@router.get("/", response_model=List[EventoResponse])
def listar_eventos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller.listar(db, skip, limit)


@router.get("/{item_id}", response_model=EventoResponse)
def obtener_eventos(item_id: int, db: Session = Depends(get_db)):
    return controller.obtener(db, item_id)


@router.post("/", response_model=EventoResponse, status_code=201)
def crear_eventos(
    datos: EventoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador", "Propietario")),
):
    return controller.crear(db, datos)


@router.put("/{item_id}", response_model=EventoResponse)
def actualizar_eventos(
    item_id: int,
    datos: EventoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador", "Propietario")),
):
    return controller.actualizar(db, item_id, datos)


@router.delete("/{item_id}")
def eliminar_eventos(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role("Administrador")),
):
    return controller.eliminar(db, item_id)
