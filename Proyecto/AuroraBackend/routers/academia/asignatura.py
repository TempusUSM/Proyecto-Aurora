from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Asignatura
from database import get_db
from schemas import AsignaturaCreate, Asignatura as AsignaturaSchema
from typing import List

router = APIRouter(
    prefix="/asignaturas",
    tags=["Asignaturas"]
)

@router.get("/", response_model=List[AsignaturaSchema])
def listar_asignaturas(db: Session = Depends(get_db)):
    return db.query(Asignatura).all()

@router.get("/{id}", response_model=AsignaturaSchema)
def obtener_asignatura(id: int, db: Session = Depends(get_db)):
    asignatura = db.query(Asignatura).filter(Asignatura.idAsignatura == id).first()
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return asignatura

@router.post("/", response_model=AsignaturaSchema)
def crear_asignatura(data: AsignaturaCreate, db: Session = Depends(get_db)):
    nueva = Asignatura(**data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=AsignaturaSchema)
def actualizar_asignatura(id: int, data: AsignaturaCreate, db: Session = Depends(get_db)):
    asignatura = db.query(Asignatura).filter(Asignatura.idAsignatura == id).first()
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    for key, value in data.model_dump().items():
        setattr(asignatura, key, value)
    db.commit()
    db.refresh(asignatura)
    return asignatura

@router.delete("/{id}")
def eliminar_asignatura(id: int, db: Session = Depends(get_db)):
    asignatura = db.query(Asignatura).filter(Asignatura.idAsignatura == id).first()
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    db.delete(asignatura)
    db.commit()
    return {"mensaje": "Asignatura eliminada"}
