from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Unidad
from database import get_db
from schemas import UnidadCreate, Unidad as UnidadSchema
from typing import List

router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"]
)

@router.get("/", response_model=List[UnidadSchema])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(Unidad).all()

@router.get("/{id}", response_model=UnidadSchema)
def obtener_unidad(id: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.idUnidad == id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return unidad

@router.post("/", response_model=UnidadSchema)
def crear_unidad(data: UnidadCreate, db: Session = Depends(get_db)):
    nueva = Unidad(**data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=UnidadSchema)
def actualizar_unidad(id: int, data: UnidadCreate, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.idUnidad == id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    for key, value in data.model_dump().items():
        setattr(unidad, key, value)
    db.commit()
    db.refresh(unidad)
    return unidad

@router.delete("/{id}")
def eliminar_unidad(id: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.idUnidad == id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    db.delete(unidad)
    db.commit()
    return {"mensaje": "Unidad eliminada"}
