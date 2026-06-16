from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import PersonaRol

router = APIRouter(prefix="/mobile", tags=["mobile"])

class LoginPayload(BaseModel):
    rut: str
    colegio_id: int

@router.post("/login")
def mobile_login(data: LoginPayload, db: Session = Depends(get_db)):
    rut_clean = data.rut.replace(".", "").strip()
    usuario = (
        db.query(PersonaRol)
        .filter(
            PersonaRol.PersonaRUT == rut_clean,
            PersonaRol.ColegioId == data.colegio_id
        )
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"message": "Login exitoso",
            "usuario_rut": rut_clean,
            "colegio_id": data.colegio_id}