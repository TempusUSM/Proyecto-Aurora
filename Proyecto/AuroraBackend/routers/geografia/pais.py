from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Pais as PaisModel
from schemas import PaisCreate, Pais
from typing import List

router = APIRouter(
    prefix="/paises",
    tags=["Paises"]
)

@router.get("/", response_model=List[Pais])
def listar_paises(db: Session = Depends(get_db)):
    return db.query(PaisModel).all()

@router.get("/{id}", response_model=Pais)
def obtener_pais(id: int, db: Session = Depends(get_db)):
    pais = db.query(PaisModel).filter(PaisModel.idPais == id).first()
    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return pais

@router.post("/", response_model=Pais)
def crear_pais(data: PaisCreate, db: Session = Depends(get_db)):
    nuevo = PaisModel(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=Pais)
def actualizar_pais(id: int, data: PaisCreate, db: Session = Depends(get_db)):
    pais = db.query(PaisModel).filter(PaisModel.idPais == id).first()
    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    for k, v in data.model_dump().items():
        setattr(pais, k, v)
    db.commit()
    db.refresh(pais)
    return pais

@router.delete("/{id}")
def eliminar_pais(id: int, db: Session = Depends(get_db)):
    pais = db.query(PaisModel).filter(PaisModel.idPais == id).first()
    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    db.delete(pais)
    db.commit()
    return {"mensaje": "País eliminado"}
