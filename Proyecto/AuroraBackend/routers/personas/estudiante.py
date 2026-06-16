from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Estudiante
from database import get_db
from schemas import EstudianteCreate, Estudiante as EstudianteSchema
from typing import List

router = APIRouter(
    prefix="/estudiantes",
    tags=["estudiantes"]
)

@router.get("/", response_model=List[EstudianteSchema])
def listar_estudiantes(db: Session = Depends(get_db)):
    return db.query(Estudiante).all()

@router.post("/", response_model=EstudianteSchema)
def crear_estudiante(estudiante_data: EstudianteCreate, db: Session = Depends(get_db)):
    if db.query(Estudiante).filter(Estudiante.RUT == estudiante_data.rut).first():
        raise HTTPException(status_code=400, detail="El estudiante ya existe")

    nuevo = Estudiante(
        RUT=estudiante_data.rut,
        ApoderadoRUT=estudiante_data.apoderado_rut,
        CursoId=estudiante_data.curso_id,
        Puntos=estudiante_data.puntos,
        PromedioGeneral=estudiante_data.promedio_general
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/{rut}", response_model=EstudianteSchema)
def obtener_estudiante(rut: str, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.RUT == rut).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.put("/{rut}", response_model=EstudianteSchema)
def actualizar_estudiante(rut: str, estudiante_data: EstudianteCreate, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.RUT == rut).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    estudiante.ApoderadoRUT = estudiante_data.apoderado_rut
    estudiante.CursoId = estudiante_data.curso_id
    estudiante.Puntos = estudiante_data.puntos
    estudiante.PromedioGeneral = estudiante_data.promedio_general

    db.commit()
    db.refresh(estudiante)
    return estudiante

@router.delete("/{rut}")
def eliminar_estudiante(rut: str, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.RUT == rut).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(estudiante)
    db.commit()
    return {"mensaje": "Estudiante eliminado"}
