from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Notas
from schemas import NotasCreate, Notas as NotasSchema
from typing import List

router = APIRouter(
    prefix="/notas",
    tags=["notas"]
)

@router.get("/", response_model=List[NotasSchema])
def listar_notas(db: Session = Depends(get_db)):
    return db.query(Notas).all()

@router.get("/{rut}/{asignatura_id}", response_model=NotasSchema)
def obtener_nota(rut: str, asignatura_id: int, db: Session = Depends(get_db)):
    nota = db.query(Notas).filter(
        Notas.EstudianteRUT == rut,
        Notas.AsignaturaId == asignatura_id
    ).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota

@router.post("/", response_model=NotasSchema)
def crear_nota(data: NotasCreate, db: Session = Depends(get_db)):
    existente = db.query(Notas).filter(
        Notas.EstudianteRUT == data.EstudianteRUT,
        Notas.AsignaturaId == data.asignatura_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una nota para este estudiante y asignatura")
    
    nueva = Notas(
        EstudianteRUT=data.EstudianteRUT,
        AsignaturaId=data.asignatura_id,
        Nota=data.nota,
        FechaEvaluacion=data.fecha_evaluacion
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.delete("/{rut}/{asignatura_id}")
def eliminar_nota(rut: str, asignatura_id: int, db: Session = Depends(get_db)):
    nota = db.query(Notas).filter(
        Notas.EstudianteRUT == rut,
        Notas.AsignaturaId == asignatura_id
    ).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.delete(nota)
    db.commit()
    return {"mensaje": "Nota eliminada"}
