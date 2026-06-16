from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Rol
from database import get_db
from schemas import RolCreate, Rol as RolSchema
from typing import List

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

@router.get("/", response_model=List[RolSchema])
def listar_roles(db: Session = Depends(get_db)):
    return db.query(Rol).all()

@router.get("/{id}", response_model=RolSchema)
def obtener_rol(id: int, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.idRol == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

@router.post("/", response_model=RolSchema)
def crear_rol(data: RolCreate, db: Session = Depends(get_db)):
    nuevo = Rol(Nombre=data.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=RolSchema)
def actualizar_rol(id: int, data: RolCreate, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.idRol == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    rol.Nombre = data.nombre
    db.commit()
    db.refresh(rol)
    return rol

@router.delete("/{id}")
def eliminar_rol(id: int, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.idRol == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.delete(rol)
    db.commit()
    return {"mensaje": "Rol eliminado"}
