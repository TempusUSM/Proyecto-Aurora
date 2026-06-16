import logging
import traceback
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Desempeno, Estudiante, Test, Sesion
from schemas import DesempenoCreate, Desempeno as DesempenoSchema

logger = logging.getLogger(__name__)

# Router web (mantiene compatibilidad con main)
router = APIRouter(prefix="/desempeno", tags=["desempeno"])

# Router móvil (extra; no rompe Web por tener prefijo distinto)
mobile_router = APIRouter(prefix="/desempenos", tags=["Desempeño (móvil)"])


# ----------------- utilidades (desde móvil) -----------------
def _detect_pk_attr_name(model) -> str:
    cols = list(model.__table__.columns)
    for c in cols:
        if c.primary_key:
            return c.name
    raise HTTPException(status_code=500, detail="No se pudo detectar la PK del modelo Estudiante.")


def _detect_points_attr_name(model) -> str:
    candidates = ["puntos", "Puntos", "PUNTOS", "glims", "Glims"]
    cols = list(model.__table__.columns)
    for cand in candidates:
        for c in cols:
            if c.name.lower() == cand.lower():
                return c.name
    for c in cols:
        lower = c.name.lower()
        if "punt" in lower or "glim" in lower:
            return c.name
    raise HTTPException(status_code=500, detail="No se pudo detectar la columna de puntos en Estudiante.")


def _safe_get_estudiante_for_update(db: Session, rut: str):
    pk_name = _detect_pk_attr_name(Estudiante)
    if hasattr(Estudiante, pk_name):
        pk_attr = getattr(Estudiante, pk_name)
    else:
        alt = next((a for a in dir(Estudiante) if a.lower() == pk_name.lower()), None)
        if alt:
            pk_attr = getattr(Estudiante, alt)
        else:
            raise HTTPException(
                status_code=500, detail=f"No se encontró atributo PK '{pk_name}' en el modelo Estudiante."
            )
    return db.query(Estudiante).filter(pk_attr == rut).with_for_update().first()


def _get_estudiante_no_lock(db: Session, rut: str):
    pk_name = _detect_pk_attr_name(Estudiante)
    if hasattr(Estudiante, pk_name):
        pk_attr = getattr(Estudiante, pk_name)
    else:
        alt = next((a for a in dir(Estudiante) if a.lower() == pk_name.lower()), None)
        if alt:
            pk_attr = getattr(Estudiante, alt)
        else:
            raise HTTPException(
                status_code=500, detail=f"No se encontró atributo PK '{pk_name}' en el modelo Estudiante."
            )
    return db.query(Estudiante).filter(pk_attr == rut).first()


def _resolve_test_id(db: Session, test_id_input: int) -> int:
    t = db.query(Test).filter(Test.idTest == test_id_input).first()
    if t:
        return int(t.idTest)
    t2 = db.query(Test).filter(Test.SesionId == test_id_input).first()
    if t2:
        return int(t2.idTest)
    raise HTTPException(status_code=404, detail=f"Test no encontrado (ni idTest ni SesionId = {test_id_input})")


def _perform_upsert_and_points(db: Session, rut: str, real_test_id: int, nota: int, detalle: str):
    """
    Inserta/actualiza Desempeno y actualiza estudiante.puntos (solo diferencia positiva).
    """
    existente = (
        db.query(Desempeno)
        .filter(Desempeno.EstudianteRUT == rut, Desempeno.TestId == real_test_id)
        .first()
    )
    old_nota = int(existente.NotaTest) if existente else 0
    added = 0

    if existente:
        existente.NotaTest = nota
        existente.Desempenio = detalle
        existente.FechaEvaluacion = date.today()
        db.add(existente)
    else:
        nueva = Desempeno(
            EstudianteRUT=rut,
            TestId=real_test_id,
            NotaTest=nota,
            Desempenio=detalle,
            FechaEvaluacion=date.today(),
        )
        db.add(nueva)

    # Garantiza INSERT/UPDATE antes de tocar estudiante
    db.flush()

    estudiante = _safe_get_estudiante_for_update(db, rut)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    puntos_col = _detect_points_attr_name(Estudiante)
    if hasattr(estudiante, puntos_col):
        current = int(getattr(estudiante, puntos_col) or 0)
        if nota > old_nota:
            added = nota - old_nota
            setattr(estudiante, puntos_col, current + added)
            db.add(estudiante)
    else:
        alt = next((a for a in dir(estudiante) if a.lower() == puntos_col.lower()), None)
        if alt:
            current = int(getattr(estudiante, alt) or 0)
            if nota > old_nota:
                added = nota - old_nota
                setattr(estudiante, alt, current + added)
                db.add(estudiante)
        else:
            raise HTTPException(
                status_code=500, detail=f"El modelo Estudiante no tiene la columna de puntos '{puntos_col}'"
            )

    db.flush()
    return added


def _upsert(payload: dict, db: Session):
    """
    Inserta/actualiza Desempeno y suma al estudiante SOLO la diferencia positiva
    entre la nueva nota y la nota previa.
    """
    try:
        rut = payload["rut"]
        test_id_input = int(payload["test_id"])
        nota = int(payload["nota_test"])
        detalle = payload.get("desempenio", "")
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="JSON inválido")

    real_test_id = _resolve_test_id(db, test_id_input)

    try:
        added = _perform_upsert_and_points(db, rut, real_test_id, nota, detalle)
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al guardar desempeño") from ie
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        tb = traceback.format_exc()
        logger.exception("Error interno en _upsert: %s", e)
        print(tb)
        raise HTTPException(status_code=500, detail=f"Error interno al procesar desempeño: {e}")

    estudiante = _get_estudiante_no_lock(db, rut)
    if not estudiante:
        raise HTTPException(status_code=500, detail="Estudiante no encontrado tras operación.")

    puntos_col = _detect_points_attr_name(Estudiante)
    if hasattr(estudiante, puntos_col):
        new_points = int(getattr(estudiante, puntos_col) or 0)
    else:
        alt = next((a for a in dir(estudiante) if a.lower() == puntos_col.lower()), None)
        new_points = int(getattr(estudiante, alt) or 0) if alt else 0

    return {
        "ok": True,
        "nota_test": nota,
        "added": added,
        "points": new_points,
        "glims": new_points,
    }


# ----------------- ENDPOINTS Web -----------------
@router.get("/", response_model=List[DesempenoSchema])
def listar_desempenos(db: Session = Depends(get_db)):
    return db.query(Desempeno).all()


@router.get("/{rut}/{test_id}", response_model=DesempenoSchema)
def obtener_desempeno(rut: str, test_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Desempeno)
        .filter(Desempeno.EstudianteRUT == rut, Desempeno.TestId == test_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Desempeño no encontrado")
    return result


@router.post("/", response_model=DesempenoSchema)
def crear_desempeno(data: DesempenoCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(Desempeno)
        .filter(Desempeno.EstudianteRUT == data.EstudianteRUT, Desempeno.TestId == data.test_id)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un registro para ese estudiante y test")

    nuevo = Desempeno(
        EstudianteRUT=data.EstudianteRUT,
        TestId=data.test_id,
        NotaTest=data.nota_test,
        Desempenio=data.desempenio,
        FechaEvaluacion=data.fecha_evaluacion,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{rut}/{test_id}")
def eliminar_desempeno(rut: str, test_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Desempeno)
        .filter(Desempeno.EstudianteRUT == rut, Desempeno.TestId == test_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Desempeño no encontrado")
    db.delete(result)
    db.commit()
    return {"mensaje": "Desempeño eliminado"}


# ----------------- ENDPOINT Móvil (upsert con puntos) -----------------
@mobile_router.post("/", status_code=status.HTTP_200_OK, summary="Upsert desempeño (móvil)")
def upsert_mobile(payload: dict, db: Session = Depends(get_db)):
    return _upsert(payload, db)

# ----------------- ENDPOINTS Móvil: progreso del estudiante -----------------
@mobile_router.get("/completadas/{rut}", summary="IDs de sesiones completadas por estudiante")
def sesiones_completadas(rut: str, db: Session = Depends(get_db)):
    """
    Devuelve una lista de IDs de sesion (sesion.idSesion) que el estudiante completó.
    Se considera 'completada' si existe un registro en `desempeno` para el Test de esa sesion.
    """
    q = (
        db.query(Test.SesionId)
        .join(Desempeno, Desempeno.TestId == Test.idTest)
        .filter(Desempeno.EstudianteRUT == rut)
        .distinct()
    )
    rows = q.all()
    # rows es una lista de tuplas [(SesionId,), ...]
    return [int(r[0]) for r in rows if r[0] is not None]


@mobile_router.get(
    "/completadas/{rut}/unidad/{unidad_id}",
    summary="IDs de sesiones completadas por estudiante en una unidad"
)
def sesiones_completadas_por_unidad(rut: str, unidad_id: int, db: Session = Depends(get_db)):
    q = (
        db.query(Test.SesionId)
        .join(Desempeno, Desempeno.TestId == Test.idTest)
        .join(Sesion, Sesion.idSesion == Test.SesionId)
        .filter(
            Desempeno.EstudianteRUT == rut,
            Sesion.UnidadId == unidad_id
        )
        .distinct()
    )
    rows = q.all()
    return [int(r[0]) for r in rows if r[0] is not None]


__all__ = ["router", "mobile_router"]
