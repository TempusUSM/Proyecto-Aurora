from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Inventario
from schemas import InventarioCreate, Inventario as InventarioSchema
from typing import List

router = APIRouter(
    prefix="/inventario",
    tags=["inventario"]
)

@router.get("/", response_model=List[InventarioSchema])
def listar_inventario(db: Session = Depends(get_db)):
    return db.query(Inventario).all()

@router.get("/{rut}/{item_id}", response_model=InventarioSchema)
def obtener_inventario(rut: str, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Inventario).filter(
        Inventario.EstudianteRUT == rut,
        Inventario.ItemId == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

@router.post("/", response_model=InventarioSchema)
def agregar_inventario(data: InventarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Inventario).filter(
        Inventario.EstudianteRUT == data.EstudianteRUT,
        Inventario.ItemId == data.item_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe ese item para este estudiante")

    nuevo = Inventario(
        EstudianteRUT=data.EstudianteRUT,
        ItemId=data.item_id,
        Cantidad=data.cantidad
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.delete("/{rut}/{item_id}")
def eliminar_inventario(rut: str, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Inventario).filter(
        Inventario.EstudianteRUT == rut,
        Inventario.ItemId == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(item)
    db.commit()
    return {"mensaje": "Item eliminado del inventario"}
