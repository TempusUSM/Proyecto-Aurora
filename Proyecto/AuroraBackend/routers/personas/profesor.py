from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Profesor
from database import get_db
from schemas import ProfesorCreate, Profesor as ProfesorSchema
from typing import List

router = APIRouter(
    prefix="/profesores",
    tags=["profesores"]
)

@router.get("/", response_model=List[ProfesorSchema])
def listar_profesores(db: Session = Depends(get_db)):
    return db.query(Profesor).all()

@router.get("/{rut}", response_model=ProfesorSchema)
def obtener_profesor(rut: str, db: Session = Depends(get_db)):
    profesor = db.query(Profesor).filter(Profesor.RUT == rut).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@router.post("/", response_model=ProfesorSchema)
def crear_profesor(profesor_data: ProfesorCreate, db: Session = Depends(get_db)):
    if db.query(Profesor).filter(Profesor.RUT == profesor_data.rut).first():
        raise HTTPException(status_code=400, detail="El profesor ya existe")

    nuevo = Profesor(
        RUT=profesor_data.rut,
        Especialidad=profesor_data.especialidad,
        TituloProfesional=profesor_data.titulo_profesional
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{rut}", response_model=ProfesorSchema)
def actualizar_profesor(rut: str, profesor_data: ProfesorCreate, db: Session = Depends(get_db)):
    profesor = db.query(Profesor).filter(Profesor.RUT == rut).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    profesor.Especialidad = profesor_data.especialidad
    profesor.TituloProfesional = profesor_data.titulo_profesional
    db.commit()
    db.refresh(profesor)
    return profesor

@router.delete("/{rut}")
def eliminar_profesor(rut: str, db: Session = Depends(get_db)):
    profesor = db.query(Profesor).filter(Profesor.RUT == rut).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    db.delete(profesor)
    db.commit()
    return {"mensaje": "Profesor eliminado"}
