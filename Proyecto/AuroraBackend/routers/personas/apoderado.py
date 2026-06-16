from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Apoderado
from database import get_db
from schemas import ApoderadoCreate, Apoderado as ApoderadoSchema
from typing import List

router = APIRouter(
    prefix="/apoderados",
    tags=["apoderados"]
)

@router.get("/", response_model=List[ApoderadoSchema])
def listar_apoderados(db: Session = Depends(get_db)):
    return db.query(Apoderado).all()

@router.get("/{rut}", response_model=ApoderadoSchema)
def obtener_apoderado(rut: str, db: Session = Depends(get_db)):
    apoderado = db.query(Apoderado).filter(Apoderado.RUT == rut).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    return apoderado

@router.post("/", response_model=ApoderadoSchema)
def crear_apoderado(apoderado_data: ApoderadoCreate, db: Session = Depends(get_db)):
    if db.query(Apoderado).filter(Apoderado.RUT == apoderado_data.rut).first():
        raise HTTPException(status_code=400, detail="El apoderado ya existe")

    nuevo = Apoderado(
        RUT=apoderado_data.rut,
        Parentesco=apoderado_data.parentesco
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{rut}", response_model=ApoderadoSchema)
def actualizar_apoderado(rut: str, apoderado_data: ApoderadoCreate, db: Session = Depends(get_db)):
    apoderado = db.query(Apoderado).filter(Apoderado.RUT == rut).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    apoderado.Parentesco = apoderado_data.parentesco
    db.commit()
    db.refresh(apoderado)
    return apoderado

@router.delete("/{rut}")
def eliminar_apoderado(rut: str, db: Session = Depends(get_db)):
    apoderado = db.query(Apoderado).filter(Apoderado.RUT == rut).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    db.delete(apoderado)
    db.commit()
    return {"mensaje": "Apoderado eliminado"}
