# routers/emociones/registroemocional.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models  import (
    RegistroEmocional as RegistroEmocionalDB,
    Emocion,
    TipoEmocionEnum,
)
from schemas import (
    RegistroEmocionalCreate,
    RegistroEmocional as RegistroEmocionalSchema,
)

# Web y móvil con prefijos distintos (coexisten sin chocar)
router        = APIRouter(prefix="/registros_emocionales",  tags=["Registros Emocionales (web)"])
mobile_router = APIRouter(prefix="/registrosemocionales",   tags=["Registros Emocionales (móvil)"])

# -------- lógica común --------
def _crear(payload: RegistroEmocionalCreate, db: Session):
    emo = db.query(Emocion).get(payload.emocion_id)
    if not emo:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    if not (1 <= payload.escala <= (emo.EscalaMax or emo.escala_max or 0)):
        raise HTTPException(status_code=400, detail=f"Escala debe estar entre 1 y {emo.EscalaMax or emo.escala_max}")

    try:
        tipo_enum = TipoEmocionEnum(payload.tipo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'pre' o 'post'")

    nuevo = RegistroEmocionalDB(
        EstudianteRUT = payload.estudiante_rut,
        EmocionId     = payload.emocion_id,
        SesionId      = payload.sesion_id,
        Tipo          = tipo_enum,
        Escala        = payload.escala,
        Contexto      = payload.contexto,
        Resumen       = payload.resumen,
        Fecha         = payload.fecha or datetime.utcnow(),
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# -------- Endpoints WEB --------
@router.get("/", response_model=list[RegistroEmocionalSchema])
def listar_web(db: Session = Depends(get_db)):
    return db.query(RegistroEmocionalDB).all()

@router.get("/{id}", response_model=RegistroEmocionalSchema)
def obtener_web(id: int, db: Session = Depends(get_db)):
    r = db.query(RegistroEmocionalDB).filter(RegistroEmocionalDB.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Registro emocional no encontrado")
    return r

@router.post("/", response_model=RegistroEmocionalSchema, status_code=status.HTTP_201_CREATED)
def crear_web(data: RegistroEmocionalCreate, db: Session = Depends(get_db)):
    return _crear(data, db)

@router.put("/{id}", response_model=RegistroEmocionalSchema)
def actualizar_web(id: int, data: RegistroEmocionalCreate, db: Session = Depends(get_db)):
    r = db.query(RegistroEmocionalDB).filter(RegistroEmocionalDB.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Registro emocional no encontrado")

    # Validaciones iguales a crear
    emo = db.query(Emocion).get(data.emocion_id)
    if not emo:
        raise HTTPException(status_code=404, detail="Emoción no encontrada")
    try:
        tipo_enum = TipoEmocionEnum(data.tipo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'pre' o 'post'")
    if not (1 <= data.escala <= (emo.EscalaMax or emo.escala_max or 0)):
        raise HTTPException(status_code=400, detail=f"Escala debe estar entre 1 y {emo.EscalaMax or emo.escala_max}")

    r.EstudianteRUT = data.estudiante_rut
    r.EmocionId     = data.emocion_id
    r.SesionId      = data.sesion_id
    r.Tipo          = tipo_enum
    r.Escala        = data.escala
    r.Contexto      = data.contexto
    r.Resumen       = data.resumen
    r.Fecha         = data.fecha or r.Fecha

    db.commit()
    db.refresh(r)
    return r

@router.delete("/{id}")
def eliminar_web(id: int, db: Session = Depends(get_db)):
    r = db.query(RegistroEmocionalDB).filter(RegistroEmocionalDB.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Registro emocional no encontrado")
    db.delete(r)
    db.commit()
    return {"mensaje": "Registro emocional eliminado"}

# -------- Endpoints MÓVIL --------
@mobile_router.get("/", response_model=list[RegistroEmocionalSchema])
def listar_mobile(
    rut: str | None = None,
    sesion_id: int | None = None,
    tipo: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(RegistroEmocionalDB)
    if rut:       q = q.filter(RegistroEmocionalDB.EstudianteRUT == rut)
    if sesion_id: q = q.filter(RegistroEmocionalDB.SesionId == sesion_id)
    if tipo:      q = q.filter(RegistroEmocionalDB.Tipo == tipo)
    return q.all()

@mobile_router.post("/", response_model=RegistroEmocionalSchema, status_code=status.HTTP_201_CREATED)
def crear_mobile(data: RegistroEmocionalCreate, db: Session = Depends(get_db)):
    return _crear(data, db)
