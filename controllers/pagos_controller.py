from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schemas.pagos_schema import PagoCreate, PagoUpdate
from services.pagos_service import pagos_service
from models.modelos import Reserva, Inscripcion

_ESTADOS_APROBADOS = {'aprobado', 'completado', 'confirmada', 'exitoso'}

def listar(db: Session, skip: int = 0, limit: int = 100):
    return pagos_service.get_all(db, skip=skip, limit=limit)

def obtener(db: Session, item_id: int):
    obj = pagos_service.get_by_id(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")
    return obj

def _confirmar_entidad_asociada(db, modelo, campo_id, valor_id, estado_pago):
    """Si el pago fue aprobado, confirma la reserva o inscripcion asociada."""
    if not valor_id or str(estado_pago).lower() not in _ESTADOS_APROBADOS:
        return
    entidad = db.query(modelo).filter(campo_id == valor_id).first()
    if entidad:
        entidad.estado = 'Confirmada'
        db.commit()

def crear(db: Session, datos: PagoCreate):
    nuevo_pago = pagos_service.create(db, datos.model_dump())
    _confirmar_entidad_asociada(db, Reserva, Reserva.id_reserva, datos.id_reserva, datos.estado)
    _confirmar_entidad_asociada(db, Inscripcion, Inscripcion.id_inscripcion, datos.id_inscripcion, datos.estado)
    return nuevo_pago

def actualizar(db: Session, item_id: int, datos: PagoUpdate):
    obj = pagos_service.update(db, item_id, datos.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")
    return obj

def eliminar(db: Session, item_id: int):
    ok = pagos_service.delete(db, item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado.")
    return {"mensaje": "Eliminado correctamente."}
