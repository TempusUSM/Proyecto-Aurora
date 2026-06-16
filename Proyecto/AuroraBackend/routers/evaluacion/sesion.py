from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sesion
from schemas import SesionCreate, SesionResponse
from typing import List

router = APIRouter(
    prefix="/sesiones",
    tags=["sesiones"]
)

@router.get("/", response_model=List[SesionResponse])
def listar_sesiones(db: Session = Depends(get_db)):
    return db.query(Sesion).all()

@router.get("/{id}", response_model=SesionResponse)
def obtener_sesion(id: int, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.idSesion == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return sesion

@router.post("/", response_model=SesionResponse)
def crear_sesion(data: SesionCreate, db: Session = Depends(get_db)):
    nueva = Sesion(
        Bitacora=data.bitacora,
        ObjetivoAprendizaje=data.objetivo_aprendizaje,
        UnidadId=data.unidad_id
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=SesionResponse)
def actualizar_sesion(id: int, data: SesionCreate, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.idSesion == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    sesion.Bitacora = data.bitacora
    sesion.ObjetivoAprendizaje = data.objetivo_aprendizaje
    sesion.UnidadId = data.unidad_id

    db.commit()
    db.refresh(sesion)
    return sesion

@router.delete("/{id}")
def eliminar_sesion(id: int, db: Session = Depends(get_db)):
    sesion = db.query(Sesion).filter(Sesion.idSesion == id).first()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    db.delete(sesion)
    db.commit()
    return {"mensaje": "Sesión eliminada"}
