# routers/points.py
from typing import Optional
from pydantic import BaseModel, conint, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Estudiante

router = APIRouter(prefix="/points", tags=["points"])

# ---------- Pydantic Schemas (deben ir antes de usarse) ----------
class ScoreIn(BaseModel):
    rut: str
    test_id: int
    nota_test: conint(ge=0)
    desempenio: Optional[str] = None

class PointsOut(BaseModel):
    rut: str
    added: int
    points: int
    glims: int
    # Pydantic v2: reemplaza orm_mode=True
    model_config = ConfigDict(from_attributes=True)

# ---------- Helpers ----------
def _detect_pk_attr_name(model) -> str:
    for c in model.__table__.columns:
        if c.primary_key:
            return c.name
    raise HTTPException(status_code=500, detail="No se pudo detectar la PK de Estudiante.")

def _detect_points_attr_name(model) -> str:
    candidates = ['puntos', 'Puntos', 'PUNTOS', 'glims', 'Glims']
    for c in model.__table__.columns:
        for cand in candidates:
            if c.name.lower() == cand.lower():
                return c.name
    for c in model.__table__.columns:
        if 'punt' in c.name.lower() or 'glim' in c.name.lower():
            return c.name
    raise HTTPException(status_code=500, detail="No se encontró columna de puntos en Estudiante.")

def _get_estudiante_for_update(db: Session, rut: str):
    pk = _detect_pk_attr_name(Estudiante)
    pk_attr = getattr(Estudiante, pk)
    return db.query(Estudiante).filter(pk_attr == rut).with_for_update().first()

# ---------- Endpoint ----------
@router.post("/add", response_model=PointsOut, status_code=status.HTTP_200_OK)
def add_points(payload: ScoreIn, db: Session = Depends(get_db)):
    """
    Suma `nota_test` al saldo del estudiante y retorna el nuevo balance.
    OJO: este endpoint no registra desempeño; solo modifica el saldo.
    """
    try:
        with db.begin():
            estudiante = _get_estudiante_for_update(db, payload.rut)
            if not estudiante:
                raise HTTPException(status_code=404, detail="Estudiante no encontrado")

            puntos_col = _detect_points_attr_name(Estudiante)
            current = int(getattr(estudiante, puntos_col) or 0)
            setattr(estudiante, puntos_col, current + int(payload.nota_test))

        # fuera del bloque (ya commiteado)
        db.refresh(estudiante)
        puntos_col = _detect_points_attr_name(Estudiante)
        new_points = int(getattr(estudiante, puntos_col) or 0)

        return PointsOut(
            rut=payload.rut,
            added=int(payload.nota_test),
            points=new_points,
            glims=new_points,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al sumar puntos: {e}")
