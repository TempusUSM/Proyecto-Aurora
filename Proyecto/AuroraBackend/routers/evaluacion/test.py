from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Test
from schemas import TestCreate, TestResponse
from typing import List

router = APIRouter(
    prefix="/tests",
    tags=["tests"]
)

@router.get("/", response_model=List[TestResponse])
def listar_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()

@router.get("/{id}", response_model=TestResponse)
def obtener_test(id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.idTest == id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    return test

@router.post("/", response_model=TestResponse)
def crear_test(data: TestCreate, db: Session = Depends(get_db)):
    nuevo = Test(
        Puntaje=data.puntaje,
        Descripcion=data.descripcion,
        SesionId=data.sesion_id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{id}", response_model=TestResponse)
def actualizar_test(id: int, data: TestCreate, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.idTest == id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    test.Puntaje = data.puntaje
    test.Descripcion = data.descripcion
    test.SesionId = data.sesion_id
    db.commit()
    db.refresh(test)
    return test

@router.delete("/{id}")
def eliminar_test(id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.idTest == id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    db.delete(test)
    db.commit()
    return {"mensaje": "Test eliminado"}
