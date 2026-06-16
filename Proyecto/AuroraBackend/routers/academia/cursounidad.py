from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import CursoUnidad
from database import get_db
from schemas import CursoUnidadCreate, CursoUnidad as CursoUnidadSchema
from typing import List

router = APIRouter(
    prefix="/cursos-unidades",
    tags=["CursoUnidad"]
)

@router.get("/", response_model=List[CursoUnidadSchema])
def listar_relaciones(db: Session = Depends(get_db)):
    return db.query(CursoUnidad).all()

@router.post("/", response_model=CursoUnidadSchema)
def crear_relacion(data: CursoUnidadCreate, db: Session = Depends(get_db)):
    existente = db.query(CursoUnidad).filter(
        CursoUnidad.CursoId == data.curso_id,
        CursoUnidad.UnidadId == data.unidad_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="La relación ya existe")

    nueva = CursoUnidad(**data.model_dump())
    db.add(nueva)
    db.commit()
    return nueva

@router.delete("/")
def eliminar_relacion(curso_id: int, unidad_id: int, db: Session = Depends(get_db)):
    relacion = db.query(CursoUnidad).filter(
        CursoUnidad.CursoId == curso_id,
        CursoUnidad.UnidadId == unidad_id
    ).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    db.delete(relacion)
    db.commit()
    return {"mensaje": "Relación eliminada"}
