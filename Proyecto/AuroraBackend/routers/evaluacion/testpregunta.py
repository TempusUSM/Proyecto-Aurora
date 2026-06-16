from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import TestPregunta
from schemas import TestPregunta, TestPreguntaCreate
from typing import List

router = APIRouter(
    prefix="/test-preguntas",
    tags=["testpreguntas"]
)

@router.get("/", response_model=List[TestPregunta])
def listar_test_preguntas(db: Session = Depends(get_db)):
    return db.query(TestPregunta).all()

@router.get("/{test_id}/{pregunta_id}", response_model=TestPregunta)
def obtener_test_pregunta(test_id: int, pregunta_id: int, db: Session = Depends(get_db)):
    rel = db.query(TestPregunta).filter(
        TestPregunta.TestId == test_id,
        TestPregunta.PreguntaId == pregunta_id
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relación Test-Pregunta no encontrada")
    return rel

@router.post("/", response_model=TestPregunta)
def crear_test_pregunta(data: TestPreguntaCreate, db: Session = Depends(get_db)):
    existente = db.query(TestPregunta).filter(
        TestPregunta.TestId == data.test_id,
        TestPregunta.PreguntaId == data.pregunta_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe esta relación Test-Pregunta")

    nueva = TestPregunta(
        TestId=data.test_id,
        PreguntaId=data.pregunta_id
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.delete("/{test_id}/{pregunta_id}")
def eliminar_test_pregunta(test_id: int, pregunta_id: int, db: Session = Depends(get_db)):
    rel = db.query(TestPregunta).filter(
        TestPregunta.TestId == test_id,
        TestPregunta.PreguntaId == pregunta_id
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    db.delete(rel)
    db.commit()
    return {"mensaje": "Relación eliminada"}
