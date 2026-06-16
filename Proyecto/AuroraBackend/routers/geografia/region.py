from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Region as RegionModel
from schemas import RegionCreate, Region
from typing import List

router = APIRouter(
    prefix="/regiones",
    tags=["Regiones"]
)

@router.get("/", response_model=List[Region])
def listar_regiones(db: Session = Depends(get_db)):
    return db.query(RegionModel).all()

@router.get("/{id}", response_model=Region)
def obtener_region(id: int, db: Session = Depends(get_db)):
    region = db.query(RegionModel).filter(RegionModel.idRegion == id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Región no encontrada")
    return region

@router.post("/", response_model=Region)
def crear_region(data: RegionCreate, db: Session = Depends(get_db)):
    nueva = RegionModel(**data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=Region)
def actualizar_region(id: int, data: RegionCreate, db: Session = Depends(get_db)):
    region = db.query(RegionModel).filter(RegionModel.idRegion == id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Región no encontrada")
    for k, v in data.model_dump().items():
        setattr(region, k, v)
    db.commit()
    db.refresh(region)
    return region

@router.delete("/{id}")
def eliminar_region(id: int, db: Session = Depends(get_db)):
    region = db.query(RegionModel).filter(RegionModel.idRegion == id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Región no encontrada")
    db.delete(region)
    db.commit()
    return {"mensaje": "Región eliminada"}
