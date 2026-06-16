from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import PAlternativas as PAlternativasModel
from schemas import PAlternativasCreate, PAlternativas
from typing import List

router = APIRouter(
    prefix="/palternativas",
    tags=["PAlternativas"]
)

@router.get("/", response_model=List[PAlternativas])
def listar_alternativas(db: Session = Depends(get_db)):
    return db.query(PAlternativasModel).all()

@router.get("/{id_pregunta}", response_model=PAlternativas)
def obtener_alternativa(id_pregunta: int, db: Session = Depends(get_db)):
    alt = db.query(PAlternativasModel).filter(PAlternativasModel.idPregunta == id_pregunta).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    return alt

@router.post("/", response_model=PAlternativas)
def crear_alternativa(datos: PAlternativasCreate, db: Session = Depends(get_db)):
    nueva = PAlternativasModel(**datos.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id_pregunta}", response_model=PAlternativas)
def actualizar_alternativa(id_pregunta: int, datos: PAlternativasCreate, db: Session = Depends(get_db)):
    alt = db.query(PAlternativasModel).filter(PAlternativasModel.idPregunta == id_pregunta).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    for key, value in datos.model_dump().items():
        setattr(alt, key, value)
    db.commit()
    db.refresh(alt)
    return alt

@router.delete("/{id_pregunta}")
def eliminar_alternativa(id_pregunta: int, db: Session = Depends(get_db)):
    alt = db.query(PAlternativasModel).filter(PAlternativasModel.idPregunta == id_pregunta).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    db.delete(alt)
    db.commit()
    return {"mensaje": "Alternativa eliminada"}
