from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Provincia as ProvinciaModel
from schemas import ProvinciaCreate, Provincia
from typing import List

router = APIRouter(
    prefix="/provincias",
    tags=["Provincias"]
)

@router.get("/", response_model=List[Provincia])
def listar_provincias(db: Session = Depends(get_db)):
    return db.query(ProvinciaModel).all()

@router.get("/{id}", response_model=Provincia)
def obtener_provincia(id: int, db: Session = Depends(get_db)):
    provincia = db.query(ProvinciaModel).filter(ProvinciaModel.idProvincia == id).first()
    if not provincia:
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    return provincia

@router.post("/", response_model=Provincia)
def crear_provincia(datos: ProvinciaCreate, db: Session = Depends(get_db)):
    nueva = ProvinciaModel(**datos.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=Provincia)
def actualizar_provincia(id: int, datos: ProvinciaCreate, db: Session = Depends(get_db)):
    provincia = db.query(ProvinciaModel).filter(ProvinciaModel.idProvincia == id).first()
    if not provincia:
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    for key, value in datos.model_dump().items():
        setattr(provincia, key, value)
    db.commit()
    db.refresh(provincia)
    return provincia

@router.delete("/{id}")
def eliminar_provincia(id: int, db: Session = Depends(get_db)):
    provincia = db.query(ProvinciaModel).filter(ProvinciaModel.idProvincia == id).first()
    if not provincia:
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    db.delete(provincia)
    db.commit()
    return {"mensaje": "Provincia eliminada"}
