from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import PersonaRol
from database import get_db
from schemas import PersonaRolCreate, PersonaRol as PersonaRolSchema
from typing import List

router = APIRouter(
    prefix="/persona_rol",
    tags=["persona_rol"]
)

@router.get("/", response_model=List[PersonaRolSchema])
def listar_personas_roles(db: Session = Depends(get_db)):
    return db.query(PersonaRol).all()

@router.get("/{persona_rut}/{rol_id}/{colegio_id}", response_model=PersonaRolSchema)
def obtener_persona_rol(persona_rut: str, rol_id: int, colegio_id: int, db: Session = Depends(get_db)):
    item = db.query(PersonaRol).filter_by(
        PersonaRUT=persona_rut,
        RolId=rol_id,
        ColegioId=colegio_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="PersonaRol no encontrado")
    return item

@router.post("/", response_model=PersonaRolSchema)
def crear_persona_rol(data: PersonaRolCreate, db: Session = Depends(get_db)):
    existente = db.query(PersonaRol).filter_by(
        PersonaRUT=data.persona_rut,
        RolId=data.rol_id,
        ColegioId=data.colegio_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe esta relación")

    nuevo = PersonaRol(
        PersonaRUT=data.persona_rut,
        RolId=data.rol_id,
        ColegioId=data.colegio_id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.delete("/{persona_rut}/{rol_id}/{colegio_id}")
def eliminar_persona_rol(persona_rut: str, rol_id: int, colegio_id: int, db: Session = Depends(get_db)):
    item = db.query(PersonaRol).filter_by(
        PersonaRUT=persona_rut,
        RolId=rol_id,
        ColegioId=colegio_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="PersonaRol no encontrado")
    db.delete(item)
    db.commit()
    return {"mensaje": "PersonaRol eliminado"}
