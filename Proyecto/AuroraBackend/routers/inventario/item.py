from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Item
from schemas import ItemCreate, Item as ItemSchema
from typing import List

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/", response_model=List[ItemSchema])
def listar_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@router.get("/{id}", response_model=ItemSchema)
def obtener_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.idItem == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

@router.post("/", response_model=ItemSchema)
def crear_item(data: ItemCreate, db: Session = Depends(get_db)):
    nuevo = Item(
        Nombre=data.nombre,
        Descripcion=data.descripcion,
        Costo=data.costo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=ItemSchema)
def actualizar_item(id: int, data: ItemCreate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.idItem == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    item.Nombre = data.nombre
    item.Descripcion = data.descripcion
    item.Costo = data.costo

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def eliminar_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.idItem == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(item)
    db.commit()
    return {"mensaje": "Item eliminado"}
