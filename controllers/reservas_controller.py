from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schemas.reservas_schema import ReservaCreate, ReservaUpdate
from services.reservas_service import reservas_service

from models.modelos import Reserva

_ESTADOS_INACTIVOS = ["Cancelada", "Cancelado", "Rechazada", "Rechazado"]

def listar(db: Session, skip: int = 0, limit: int = 100):
    return reservas_service.get_all(db, skip=skip, limit=limit)

def obtener(db: Session, item_id: int):
    obj = reservas_service.get_by_id(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")
    return obj

def _validar_horario(hora_inicio, hora_fin):
    """Valida que la hora fin sea posterior a la hora inicio."""
    if hora_fin <= hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de finalizacion debe ser posterior a la hora de inicio."
        )

def _verificar_solapamiento(db, id_cancha, fecha, hora_inicio, hora_fin, excluir_id=None):
    """Verifica que no exista otra reserva activa en la misma franja horaria."""
    query = db.query(Reserva).filter(
        Reserva.id_cancha == id_cancha,
        Reserva.fecha == fecha,
        Reserva.estado.notin_(_ESTADOS_INACTIVOS),
        Reserva.hora_inicio < hora_fin,
        Reserva.hora_fin > hora_inicio,
    )
    if excluir_id is not None:
        query = query.filter(Reserva.id_reserva != excluir_id)
    
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cancha ya cuenta con una reserva activa en esa franja horaria. Elige otro horario o pista."
        )

def crear(db: Session, datos: ReservaCreate):
    _validar_horario(datos.hora_inicio, datos.hora_fin)
    _verificar_solapamiento(db, datos.id_cancha, datos.fecha, datos.hora_inicio, datos.hora_fin)
    return reservas_service.create(db, datos.model_dump())

def actualizar(db: Session, item_id: int, datos: ReservaUpdate):
    obj = reservas_service.get_by_id(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")

    datos_dict = datos.model_dump(exclude_unset=True)
    cancha_id = datos_dict.get("id_cancha", obj.id_cancha)
    fecha_res = datos_dict.get("fecha", obj.fecha)
    inicio = datos_dict.get("hora_inicio", obj.hora_inicio)
    fin = datos_dict.get("hora_fin", obj.hora_fin)

    _validar_horario(inicio, fin)
    _verificar_solapamiento(db, cancha_id, fecha_res, inicio, fin, excluir_id=item_id)
    return reservas_service.update(db, item_id, datos_dict)

def eliminar(db: Session, item_id: int):
    ok = reservas_service.delete(db, item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")
    return {"mensaje": "Eliminado correctamente."}
