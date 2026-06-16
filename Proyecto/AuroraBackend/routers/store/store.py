# routers/store/store.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Estudiante, Item, Inventario

router = APIRouter(prefix="/store", tags=["store"])

# ---------- Helpers de nombres de columnas (por si difieren en mayúsculas) ----------
def _find_col(model, candidates: list[str], contains: list[str] | None = None) -> str:
    cols = [c.name for c in model.__table__.columns]
    # 1) match exacto (case-insensitive)
    for cand in candidates:
        for col in cols:
            if col.lower() == cand.lower():
                return col
    # 2) match por contiene (case-insensitive)
    if contains:
        for col in cols:
            name = col.lower()
            if any(tok.lower() in name for tok in contains):
                return col
    raise HTTPException(
        status_code=500,
        detail=f"No se encontró columna esperada en {model.__name__} (candidatos={candidates}, contains={contains})",
    )

def _pk_estudiante() -> str:
    return _find_col(Estudiante, ["RUT", "rut"], ["rut"])

def _points_col() -> str:
    return _find_col(Estudiante, ["Puntos", "puntos", "glims", "Glims"], ["punt", "glim"])

def _item_pk() -> str:
    return _find_col(Item, ["idItem", "id", "item_id"], ["id"])

def _item_tipo_col() -> str | None:
    try:
        return _find_col(Item, ["Tipo", "tipo"], ["tipo"])
    except HTTPException:
        return None

def _item_nombre_col() -> str:
    return _find_col(Item, ["Nombre", "nombre", "name"], ["nom", "name"])

def _item_desc_col() -> str | None:
    # opcional
    try:
        return _find_col(Item, ["Descripcion", "descripcion", "description"], ["desc"])
    except HTTPException:
        return None

def _item_costo_col() -> str:
    return _find_col(Item, ["Costo", "costo", "price"], ["costo", "price"])

def _item_asset_col() -> str | None:
    # ✅ ahora reconoce la columna REAL "Imagen"
    try:
        return _find_col(Item, ["Imagen", "imagen", "asset_ref", "assetRef", "AssetRef"], ["img", "asset", "image"])
    except HTTPException:
        return None

def _inv_estudiante_col() -> str:
    return _find_col(Inventario, ["EstudianteRUT", "rut", "RUT"], ["rut"])

def _inv_item_col() -> str:
    return _find_col(Inventario, ["ItemId", "item_id", "idItem"], ["item"])

# ---------- Helper: normaliza y arma URL absoluta de la imagen ----------
def _abs_url(request: Request, raw: str | None) -> str | None:
    """
    Convierte lo que haya en BD (p. ej. 'aurora_azul.png' | 'skins/aurora_azul.png' | 'statics/skins/aurora_azul.png')
    en una URL absoluta servida por /statics. Si ya es http(s), la retorna tal cual.
    """
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None

    if s.startswith("http://") or s.startswith("https://"):
        return s

    s = s.lstrip("/")
    if s.startswith("statics/"):
        path = s
    elif s.startswith("skins/"):
        path = f"statics/{s}"
    else:
        path = f"statics/skins/{s}"

    base = str(request.base_url)  # incluye slash final
    return f"{base}{path}"

# ---------- Schemas ----------
class PurchaseIn(BaseModel):
    rut: str
    item_id: int

class PurchaseOut(BaseModel):
    ok: bool
    new_balance: int

# ---------- Endpoints públicos ----------

@router.get("/skins")
def list_skins(request: Request, db: Session = Depends(get_db)):
    tipo_col = _item_tipo_col()
    id_col = _item_pk()
    nombre_col = _item_nombre_col()
    desc_col = _item_desc_col()
    costo_col = _item_costo_col()
    asset_col = _item_asset_col()

    q = db.query(Item)
    if tipo_col:
        q = q.filter(getattr(Item, tipo_col) == "skin")  # solo si existe columna

    items = q.all()
    out = []
    for it in items:
        raw_asset = getattr(it, asset_col) if asset_col else None
        out.append({
            "id": getattr(it, id_col),
            "nombre": getattr(it, nombre_col),
            "descripcion": getattr(it, desc_col) if desc_col else None,
            "costo": getattr(it, costo_col),
            "tipo": getattr(it, tipo_col) if tipo_col else "skin",  # fallback
            "asset_ref": _abs_url(request, raw_asset),              # ✅ ahora siempre URL usable
        })
    return out

@router.get("/balance/{rut}")
def get_balance(rut: str, db: Session = Depends(get_db)):
    pk = _pk_estudiante()
    pts = _points_col()
    est = db.query(Estudiante).filter(getattr(Estudiante, pk) == rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"glims": int(getattr(est, pts) or 0)}

@router.get("/inventory/{rut}")
def get_inventory(rut: str, request: Request, db: Session = Depends(get_db)):
    inv_rut = _inv_estudiante_col()
    inv_item = _inv_item_col()

    id_col = _item_pk()
    nombre_col = _item_nombre_col()
    desc_col = _item_desc_col()
    costo_col = _item_costo_col()
    tipo_col = _item_tipo_col()
    asset_col = _item_asset_col()

    q = (
        db.query(Item)
        .join(Inventario, getattr(Inventario, inv_item) == getattr(Item, id_col))
        .filter(getattr(Inventario, inv_rut) == rut)
    )
    items = q.all()
    return [
        {
            "id": getattr(it, id_col),
            "nombre": getattr(it, nombre_col),
            "descripcion": getattr(it, desc_col) if desc_col else None,
            "costo": getattr(it, costo_col),
            "tipo": getattr(it, tipo_col) if tipo_col else "skin",  # fallback
            "asset_ref": _abs_url(request, getattr(it, asset_col) if asset_col else None),  # ✅
        }
        for it in items
    ]

@router.post("/purchase", response_model=PurchaseOut, status_code=status.HTTP_200_OK)
def purchase(payload: PurchaseIn, db: Session = Depends(get_db)):
    pk = _pk_estudiante()
    pts = _points_col()

    id_col = _item_pk()
    costo_col = _item_costo_col()
    tipo_col = _item_tipo_col()

    inv_rut = _inv_estudiante_col()
    inv_item = _inv_item_col()

    # 1) Buscar item
    item = (
        db.query(Item)
        .filter(getattr(Item, id_col) == payload.item_id)
        .limit(1)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")

    # ✅ si no existe columna 'tipo', asumimos 'skin' para no romper
    if tipo_col:
        if (getattr(item, tipo_col) or "").lower() != "skin":
            raise HTTPException(status_code=400, detail="Sólo se pueden comprar skins")

    costo = int(getattr(item, costo_col) or 0)

    # 2) Lock del estudiante y ver saldo
    est = (
        db.query(Estudiante)
        .filter(getattr(Estudiante, pk) == payload.rut)
        .with_for_update()  # lock de fila
        .first()
    )
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    saldo = int(getattr(est, pts) or 0)

    # 3) ¿ya lo tiene?
    ya_tiene = (
        db.query(Inventario)
        .filter(
            getattr(Inventario, inv_rut) == payload.rut,
            getattr(Inventario, inv_item) == payload.item_id,
        )
        .first()
    )
    if ya_tiene:
        # Idempotente: no cobramos de nuevo
        return PurchaseOut(ok=True, new_balance=saldo)

    # 4) Validar saldo
    if saldo < costo:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    # 5) Descontar y crear fila en Inventario
    try:
        setattr(est, pts, saldo - costo)
        inv = Inventario()
        setattr(inv, inv_rut, payload.rut)
        setattr(inv, inv_item, payload.item_id)
        db.add(inv)

        db.flush()   # asegura INSERTs/UPDATEs
        db.commit()  # fin transacción
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya posees esta skin")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno en purchase: {e}")

    # 6) Traer saldo nuevo
    nuevo_saldo = int(getattr(est, pts) or 0)
    return PurchaseOut(ok=True, new_balance=nuevo_saldo)
