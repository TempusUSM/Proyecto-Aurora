from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Curso
from database import get_db
from schemas import CursoCreate, Curso as CursoSchema
from typing import List

router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"]
)

@router.get("/", response_model=List[CursoSchema])
def listar_cursos(db: Session = Depends(get_db)):
    return db.query(Curso).all()

@router.get("/{id}", response_model=CursoSchema)
def obtener_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.idCurso == id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@router.post("/", response_model=CursoSchema)
def crear_curso(curso_data: CursoCreate, db: Session = Depends(get_db)):
    nuevo = Curso(**curso_data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=CursoSchema)
def actualizar_curso(id: int, curso_data: CursoCreate, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.idCurso == id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    for key, value in curso_data.model_dump().items():
        setattr(curso, key, value)
    db.commit()
    db.refresh(curso)
    return curso

@router.delete("/{id}")
def eliminar_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.idCurso == id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    db.delete(curso)
    db.commit()
    return {"mensaje": "Curso eliminado"}
