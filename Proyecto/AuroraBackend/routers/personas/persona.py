from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Persona
from database import get_db
from schemas import PersonaCreate, Persona as PersonaSchema
from typing import List

router = APIRouter(
    prefix="/personas",
    tags=["personas"]
)

@router.get("/", response_model=List[PersonaSchema])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(Persona).all()

@router.get("/{rut}", response_model=PersonaSchema)
def obtener_persona(rut: str, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.RUT == rut).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@router.post("/", response_model=PersonaSchema)
def crear_persona(persona_data: PersonaCreate, db: Session = Depends(get_db)):
    if db.query(Persona).filter(Persona.RUT == persona_data.rut).first():
        raise HTTPException(status_code=400, detail="La persona ya existe")

    nueva = Persona(
        RUT=persona_data.rut,
        Nombres=persona_data.nombres,
        ApellidoPaterno=persona_data.apellido_paterno,
        ApellidoMaterno=persona_data.apellido_materno,
        ComunaId=persona_data.comuna_id,
        Telefono=persona_data.telefono,
        Correo=persona_data.correo,
        Direccion=persona_data.direccion,
        FechaNacimiento=persona_data.fecha_nacimiento,
        Genero=persona_data.genero,
        Estado=persona_data.estado
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{rut}", response_model=PersonaSchema)
def actualizar_persona(rut: str, persona_data: PersonaCreate, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.RUT == rut).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    persona.Nombres = persona_data.nombres
    persona.ApellidoPaterno = persona_data.apellido_paterno
    persona.ApellidoMaterno = persona_data.apellido_materno
    persona.ComunaId = persona_data.comuna_id
    persona.Telefono = persona_data.telefono
    persona.Correo = persona_data.correo
    persona.Direccion = persona_data.direccion
    persona.FechaNacimiento = persona_data.fecha_nacimiento
    persona.Genero = persona_data.genero
    persona.Estado = persona_data.estado

    db.commit()
    db.refresh(persona)
    return persona

@router.delete("/{rut}")
def eliminar_persona(rut: str, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.RUT == rut).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db.delete(persona)
    db.commit()
    return {"mensaje": "Persona eliminada"}
