from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Comuna as ComunaModel
from schemas import ComunaCreate, Comuna
from typing import List

router = APIRouter(
    prefix="/comunas",
    tags=["Comunas"]
)

@router.get("/", response_model=List[Comuna])
def listar_comunas(db: Session = Depends(get_db)):
    return db.query(ComunaModel).all()

@router.get("/{id}", response_model=Comuna)
def obtener_comuna(id: int, db: Session = Depends(get_db)):
    comuna = db.query(ComunaModel).filter(ComunaModel.idComuna == id).first()
    if not comuna:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    return comuna

@router.post("/", response_model=Comuna)
def crear_comuna(datos: ComunaCreate, db: Session = Depends(get_db)):
    nueva = ComunaModel(**datos.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=Comuna)
def actualizar_comuna(id: int, datos: ComunaCreate, db: Session = Depends(get_db)):
    comuna = db.query(ComunaModel).filter(ComunaModel.idComuna == id).first()
    if not comuna:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    for key, value in datos.model_dump().items():
        setattr(comuna, key, value)
    db.commit()
    db.refresh(comuna)
    return comuna

@router.delete("/{id}")
def eliminar_comuna(id: int, db: Session = Depends(get_db)):
    comuna = db.query(ComunaModel).filter(ComunaModel.idComuna == id).first()
    if not comuna:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    db.delete(comuna)
    db.commit()
    return {"mensaje": "Comuna eliminada"}
