from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Colegio as ColegioModel
from schemas import ColegioCreate, Colegio
from typing import List

router = APIRouter(
    prefix="/colegios",
    tags=["Colegios"]
)

@router.get("/", response_model=List[Colegio])
def listar_colegios(db: Session = Depends(get_db)):
    return db.query(ColegioModel).all()

@router.get("/{id}", response_model=Colegio)
def obtener_colegio(id: int, db: Session = Depends(get_db)):
    colegio = db.query(ColegioModel).filter(ColegioModel.idColegio == id).first()
    if not colegio:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    return colegio

@router.post("/", response_model=Colegio)
def crear_colegio(datos: ColegioCreate, db: Session = Depends(get_db)):
    nuevo = ColegioModel(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=Colegio)
def actualizar_colegio(id: int, datos: ColegioCreate, db: Session = Depends(get_db)):
    colegio = db.query(ColegioModel).filter(ColegioModel.idColegio == id).first()
    if not colegio:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    for key, value in datos.model_dump().items():
        setattr(colegio, key, value)
    db.commit()
    db.refresh(colegio)
    return colegio

@router.delete("/{id}")
def eliminar_colegio(id: int, db: Session = Depends(get_db)):
    colegio = db.query(ColegioModel).filter(ColegioModel.idColegio == id).first()
    if not colegio:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    db.delete(colegio)
    db.commit()
    return {"mensaje": "Colegio eliminado"}
