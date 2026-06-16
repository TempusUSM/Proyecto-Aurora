from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path

from database import get_db
from models import Material, Estudiante
from schemas import Material as MaterialSchema, MaterialCreate

router = APIRouter(prefix="/material", tags=["Material"])

# --------- LISTAR ----------
@router.get("/", response_model=list[MaterialSchema])
def listar_materiales(
    curso_id: int | None = None,
    estudiante_rut: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista materiales.
    - Si pasas `estudiante_rut`, se deduce su `CursoId`.
    - Si pasas `curso_id`, filtra por ese curso.
    - Si no pasas nada, devuelve todos.
    """
    if estudiante_rut:
        est = db.query(Estudiante).filter_by(RUT=estudiante_rut).first()
        if not est:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        curso_id = est.CursoId

    q = db.query(Material)
    if curso_id is not None:
        q = q.filter_by(CursoId=curso_id)

    return q.order_by(Material.SubidoEn.desc()).all()


# --------- OBTENER UNO ----------
@router.get("/{material_id}", response_model=MaterialSchema)
def obtener_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(Material).filter_by(idMaterial=material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return mat


# --------- CREAR (JSON) ----------
@router.post("/", response_model=MaterialSchema)
def crear_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    mat = Material(
        Titulo=payload.titulo,
        Descripcion=payload.descripcion,
        ArchivoPath=payload.archivo_path,
        CursoId=payload.curso_id,
        ProfesorRUT=payload.profesor_rut,
        SubidoEn=payload.subido_en,  # puede venir None y la BD asigna CURRENT_TIMESTAMP
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return mat


# --------- CREAR con UPLOAD (opcional) ----------
@router.post("/upload", response_model=MaterialSchema)
async def subir_material(
    file: UploadFile = File(...),
    titulo: str = Form(...),
    curso_id: int = Form(...),
    profesor_rut: str = Form(...),
    descripcion: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Sube un archivo a 'uploads/materials' y crea el registro en BD con la ruta.
    """
    base_dir = Path("uploads") / "materials"
    base_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix or ""
    filename = f"{uuid4().hex}{ext}"
    save_path = base_dir / filename

    with save_path.open("wb") as f:
        f.write(await file.read())

    mat = Material(
        Titulo=titulo,
        Descripcion=descripcion,
        ArchivoPath=str(save_path).replace("\\", "/"),
        CursoId=curso_id,
        ProfesorRUT=profesor_rut,
        # SubidoEn: lo pone la BD por DEFAULT CURRENT_TIMESTAMP
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return mat


# --------- ELIMINAR ----------
@router.delete("/{material_id}")
def eliminar_material(material_id: int, db: Session = Depends(get_db)):
    mat = db.query(Material).filter_by(idMaterial=material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    db.delete(mat)
    db.commit()
    return {"ok": True}
