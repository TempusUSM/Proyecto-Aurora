from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Pregunta as PreguntaModel
from schemas import PreguntaCreate, Pregunta
from typing import List

router = APIRouter(
    prefix="/preguntas",
    tags=["Preguntas"]
)

@router.get("/", response_model=List[Pregunta])
def listar_preguntas(db: Session = Depends(get_db)):
    return db.query(PreguntaModel).all()

@router.get("/{id}", response_model=Pregunta)
def obtener_pregunta(id: int, db: Session = Depends(get_db)):
    pregunta = db.query(PreguntaModel).filter(PreguntaModel.idPregunta == id).first()
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return pregunta

@router.post("/", response_model=Pregunta)
def crear_pregunta(pregunta_data: PreguntaCreate, db: Session = Depends(get_db)):
    nueva = PreguntaModel(**pregunta_data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=Pregunta)
def actualizar_pregunta(id: int, pregunta_data: PreguntaCreate, db: Session = Depends(get_db)):
    pregunta = db.query(PreguntaModel).filter(PreguntaModel.idPregunta == id).first()
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    for key, value in pregunta_data.model_dump().items():
        setattr(pregunta, key, value)
    db.commit()
    db.refresh(pregunta)
    return pregunta

@router.delete("/{id}")
def eliminar_pregunta(id: int, db: Session = Depends(get_db)):
    pregunta = db.query(PreguntaModel).filter(PreguntaModel.idPregunta == id).first()
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    db.delete(pregunta)
    db.commit()
    return {"mensaje": "Pregunta eliminada"}
