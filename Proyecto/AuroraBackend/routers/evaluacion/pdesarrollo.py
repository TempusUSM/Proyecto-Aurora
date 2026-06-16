from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import PDesarrollo as PDesarrolloModel
from schemas import PDesarrolloCreate, PDesarrollo
from typing import List

router = APIRouter(
    prefix="/pdesarrollo",
    tags=["PDesarrollo"]
)

@router.get("/", response_model=List[PDesarrollo])
def listar_desarrollos(db: Session = Depends(get_db)):
    return db.query(PDesarrolloModel).all()

@router.get("/{id}", response_model=PDesarrollo)
def obtener_desarrollo(id: int, db: Session = Depends(get_db)):
    obj = db.query(PDesarrolloModel).filter(PDesarrolloModel.idPDesarrollo == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pregunta de desarrollo no encontrada")
    return obj

@router.post("/", response_model=PDesarrollo)
def crear_desarrollo(datos: PDesarrolloCreate, db: Session = Depends(get_db)):
    nuevo = PDesarrolloModel(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=PDesarrollo)
def actualizar_desarrollo(id: int, datos: PDesarrolloCreate, db: Session = Depends(get_db)):
    obj = db.query(PDesarrolloModel).filter(PDesarrolloModel.idPDesarrollo == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pregunta de desarrollo no encontrada")
    for k, v in datos.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
def eliminar_desarrollo(id: int, db: Session = Depends(get_db)):
    obj = db.query(PDesarrolloModel).filter(PDesarrolloModel.idPDesarrollo == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pregunta de desarrollo no encontrada")
    db.delete(obj)
    db.commit()
    return {"mensaje": "Pregunta de desarrollo eliminada"}
