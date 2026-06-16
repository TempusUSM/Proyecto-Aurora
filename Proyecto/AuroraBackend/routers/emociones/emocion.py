from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Emocion as EmocionModel
from schemas import EmocionCreate, Emocion
from typing import List

router = APIRouter(
    prefix="/emociones",
    tags=["Emociones"]
)

@router.get("/", response_model=List[Emocion])
def listar_emociones(db: Session = Depends(get_db)):
    return db.query(EmocionModel).all()

@router.get("/{id}", response_model=Emocion)
def obtener_emocion(id: int, db: Session = Depends(get_db)):
    emocion = db.query(EmocionModel).filter(EmocionModel.idEmocion == id).first()
    if not emocion:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    return emocion

@router.post("/", response_model=Emocion)
def crear_emocion(data: EmocionCreate, db: Session = Depends(get_db)):
    nueva = EmocionModel(**data.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{id}", response_model=Emocion)
def actualizar_emocion(id: int, data: EmocionCreate, db: Session = Depends(get_db)):
    emocion = db.query(EmocionModel).filter(EmocionModel.idEmocion == id).first()
    if not emocion:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    for k, v in data.model_dump().items():
        setattr(emocion, k, v)
    db.commit()
    db.refresh(emocion)
    return emocion

@router.delete("/{id}")
def eliminar_emocion(id: int, db: Session = Depends(get_db)):
    emocion = db.query(EmocionModel).filter(EmocionModel.idEmocion == id).first()
    if not emocion:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    db.delete(emocion)
    db.commit()
    return {"mensaje": "Emoción eliminada"}
