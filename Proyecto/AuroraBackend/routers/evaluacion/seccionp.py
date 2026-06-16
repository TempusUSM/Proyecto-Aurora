from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import SeccionP
from schemas import SeccionPCreate, SeccionP as SeccionPSchema

router = APIRouter(
    prefix="/seccionp",
    tags=["seccionp"]
)

@router.get("/", response_model=List[SeccionPSchema])
def listar_secciones(db: Session = Depends(get_db)):
    return db.query(SeccionP).all()

@router.get("/{id}", response_model=SeccionPSchema)
def obtener_seccion(id: int, db: Session = Depends(get_db)):
    seccion = db.query(SeccionP).filter(SeccionP.idSeccionP == id).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    return seccion

@router.post("/", response_model=SeccionPSchema)
def crear_seccion(data: SeccionPCreate, db: Session = Depends(get_db)):
    nueva = SeccionP(
        Foto=data.foto,
        Descripcion=data.descripcion
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=SeccionPSchema)
def actualizar_seccion(id: int, data: SeccionPCreate, db: Session = Depends(get_db)):
    seccion = db.query(SeccionP).filter(SeccionP.idSeccionP == id).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")

    seccion.Foto = data.foto
    seccion.Descripcion = data.descripcion

    db.commit()
    db.refresh(seccion)
    return seccion

@router.delete("/{id}")
def eliminar_seccion(id: int, db: Session = Depends(get_db)):
    seccion = db.query(SeccionP).filter(SeccionP.idSeccionP == id).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    db.delete(seccion)
    db.commit()
    return {"mensaje": "Sección eliminada"}
