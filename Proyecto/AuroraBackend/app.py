
import logging
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import joinedload, Session
from sqlalchemy.exc import IntegrityError

from datetime import datetime, date
from pathlib import Path
from typing import Optional

import mimetypes
import base64
from routers.chatbot.chatbot import router as chatbot_router
from routers.dashboard_profesor import dashboard_emocional
from pydantic import BaseModel



from database import get_db
from models import (
    Estudiante,
    Asignatura,
    Unidad,
    Persona,
    Sesion,
    PersonaRol,
    RegistroEmocional,
    TipoEmocionEnum,
    Pregunta,
    Profesor,
    TipoPreguntaEnum,
    Test,
    Desempeno,
    TestPregunta,
    PAlternativas,
    PDesarrollo,
    SeccionP,
    Item,
    Inventario,
    Material,
)

# Routers Web
from routers.geografia import pais, region, provincia, comuna, colegio
from routers.personas import persona, rol, personarol, profesor, apoderado, estudiante
from routers.academia import curso, asignatura, unidad, cursounidad, material
from routers.emociones import emocion, registroemocional
from routers.evaluacion import test, sesion, pregunta, testpregunta, palternativas, pdesarrollo, seccionp
from routers.resultados import notas, desempeno
from routers.inventario import item, inventario
from routers.chatbot import router as chatbot_router
from routers.dashboard_profesor import dashboard_emocional

# Routers Móvil (tuyos)
from routers.mobile import auth as mobile_auth
from routers.store.store import router as store_router
from routers.points import router as points_router

# -------------------------------------------------------------------
# FastAPI base
# -------------------------------------------------------------------
app = FastAPI()
app.include_router(chatbot_router)

# Middleware de sesión real
app.add_middleware(SessionMiddleware, secret_key="supersecreto")

templates = Jinja2Templates(directory="templates")

BASE_DIR   = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

app.mount("/statics", StaticFiles(directory="statics"), name="statics")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Registro de routers (Web primero, luego móvil)
# -------------------------------------------------------------------
app.include_router(pais.router)
app.include_router(region.router)
app.include_router(provincia.router)
app.include_router(comuna.router)
app.include_router(colegio.router)

app.include_router(persona.router)
app.include_router(rol.router)
app.include_router(personarol.router)
app.include_router(profesor.router)
app.include_router(apoderado.router)
app.include_router(estudiante.router)

app.include_router(curso.router)
app.include_router(asignatura.router)
app.include_router(unidad.router)
app.include_router(cursounidad.router)
app.include_router(material.router)

app.include_router(emocion.router)
app.include_router(registroemocional.router)

app.include_router(test.router)
app.include_router(sesion.router)
app.include_router(pregunta.router)
app.include_router(testpregunta.router)
app.include_router(palternativas.router)
app.include_router(pdesarrollo.router)
app.include_router(seccionp.router)

app.include_router(notas.router)
app.include_router(desempeno.router)

app.include_router(item.router)
app.include_router(inventario.router)

# Routers móviles
app.include_router(mobile_auth.router)
app.include_router(desempeno.mobile_router)          # upsert móvil
app.include_router(registroemocional.mobile_router)  # endpoints móviles de emociones
app.include_router(store_router)                     # tienda
app.include_router(points_router)                    # puntos

app.include_router(chatbot_router) 


app.include_router(dashboard_emocional.router)


# -------------------------------------------------------------------
# Helpers comunes
# -------------------------------------------------------------------
def common_context(request: Request, db: Session) -> dict:
    """Contexto base para navbar (glims/skin) en TODAS las páginas."""
    rut = request.session.get("rut")
    glims = 0
    skin_activa = None
    if rut:
        est = db.query(Estudiante).filter_by(RUT=rut).first()
        if est:
            glims = est.Puntos or 0
        try:
            skin_activa = get_skin_activa(db, rut)
        except Exception:
            skin_activa = None
    return {"glims": glims, "skin_activa": skin_activa, "usuario_rut": rut}

def get_estudiante(db: Session, rut: str) -> Estudiante:
    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return est

def get_test_by_sesion(db: Session, sesion_id: int) -> Optional[Test]:
    return db.query(Test).filter_by(SesionId=sesion_id).first()

def is_session_completed(db: Session, rut: str, sesion_id: int) -> bool:
    pre = db.query(RegistroEmocional).filter_by(
        EstudianteRUT=rut, SesionId=sesion_id, Tipo=TipoEmocionEnum.pre
    ).first()
    post = db.query(RegistroEmocional).filter_by(
        EstudianteRUT=rut, SesionId=sesion_id, Tipo=TipoEmocionEnum.post
    ).first()
    test = get_test_by_sesion(db, sesion_id)
    has_score = False
    if test:
        has_score = db.query(Desempeno).filter_by(
            EstudianteRUT=rut, TestId=test.idTest
        ).first() is not None
    return bool(pre and post and has_score)

def is_unit_unlocked(db: Session, rut: str, unidad: Unidad) -> bool:
    """Desbloquea unidad 1; las siguientes solo si todas las sesiones de la unidad anterior están completas."""
    unidades = (
        db.query(Unidad)
        .filter_by(AsignaturaId=unidad.AsignaturaId)
        .order_by(Unidad.Numero.asc())
        .all()
    )
    if not unidades or unidades[0].idUnidad == unidad.idUnidad:
        return True
    prev = None
    for i, u in enumerate(unidades):
        if u.idUnidad == unidad.idUnidad and i > 0:
            prev = unidades[i - 1]
            break
    if not prev:
        return True
    sesiones_prev = db.query(Sesion).filter_by(UnidadId=prev.idUnidad).all()
    return all(is_session_completed(db, rut, s.idSesion) for s in sesiones_prev)

def get_preguntas_de_test(db: Session, test_id: int) -> list[dict]:
    thp = db.query(TestPregunta).filter_by(TestId=test_id).all()
    items = []
    for rel in thp:
        p = db.query(Pregunta).get(rel.PreguntaId)
        if not p:
            continue
        if p.Tipo == "Alternativa":
            alt = db.query(PAlternativas).filter_by(idPregunta=p.idPregunta).first()
            items.append({
                "tipo": "alternativa",
                "pregunta_id": p.idPregunta,
                "puntaje": p.Puntaje,
                "enunciado": alt.Enunciado if alt else "",
                "opciones": [
                    ("PA", alt.PA if alt else None),
                    ("PB", alt.PB if alt else None),
                    ("PC", alt.PC if alt else None),
                    ("PD", alt.PD if alt else None),
                ],
                "correcta": alt.Correcta if alt else None,
            })
        else:
            des = db.query(PDesarrollo).filter_by(idPregunta=p.idPregunta).first()
            items.append({
                "tipo": "desarrollo",
                "pregunta_id": p.idPregunta,
                "puntaje": p.Puntaje,
                "enunciado": des.Enunciado if des else "",
                "esperada": des.RespuestaEsperada if des else "",
            })
    return items

def compute_score(items: list[dict], respuestas: dict) -> int:
    total = 0
    for it in items:
        pid = str(it["pregunta_id"])
        if it["tipo"] == "alternativa":
            if str(respuestas.get(pid, "")).strip() == str(it.get("correcta", "")):
                total += int(it["puntaje"])
        else:
            if str(respuestas.get(pid, "")).strip():
                total += int(it["puntaje"])
    return total

def get_skin_activa(db: Session, rut: str):
    """
    Si la BD tiene columna Estudiante.SkinActivaId, se usa.
    Si no, devuelve None (o podrías inferir una por inventario).
    """
    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est or not hasattr(est, "SkinActivaId") or not est.SkinActivaId:
        return None
    return db.query(Item).filter_by(idItem=est.SkinActivaId).first()

def _safe_join_uploads(rel_path: str) -> Path:
    p = (UPLOAD_DIR / rel_path).resolve()
    if not str(p).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Ruta inválida")
    return p

def _imagen_seccion_base64(db, seccion_id: Optional[int]) -> Optional[str]:
    """Devuelve imagen de Sección (BLOB) como data URL base64, o None."""
    if not seccion_id:
        return None
    sec = db.query(SeccionP).filter_by(idSeccionP=seccion_id).first()
    if not sec or not sec.Foto:
        return None
    try:
        b64 = base64.b64encode(sec.Foto).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return None

def glims_delta_from_scores(new_score: int, prev_best: int | None) -> int:
    prev_best = prev_best or 0
    delta = int(round(new_score - prev_best))
    return max(0, delta)

# ---------------------- LOGIN ----------------------
@app.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ---------------------- LOGIN ----------------------
@app.post("/", response_class=RedirectResponse)
@app.post("/")
def login_submit(request: Request, rut: str = Form(...), db: Session = Depends(get_db)):
    rut_clean = rut.replace(".", "").strip()
    logging.info(f"Login intent: RUT = {rut_clean}")

    # Buscamos rol en PersonaRol
    rol_persona = db.query(PersonaRol).filter_by(PersonaRUT=rut_clean).first()
    if not rol_persona:
        logging.warning(f"No se encontró rol para RUT: {rut_clean}")
        return RedirectResponse(url="/", status_code=302)
    
    logging.info(f"Rol encontrado: {rol_persona.RolId}")

    # Guardamos sesión
    request.session["rut"] = rut_clean

    if rol_persona.RolId == 1:
        request.session["rol"] = "estudiante"
        logging.info(f"Redirigiendo a dashboard de estudiante")
        return RedirectResponse(url="/dashboard", status_code=302)
    elif rol_persona.RolId == 2:
        request.session["rol"] = "profesor"

        # Comprobamos que exista el profesor en la tabla Profesor
        profesor = db.query(Profesor).filter_by(RUT=rut_clean).first()
        if not profesor:
            logging.error(f"Usuario con RolId=2 pero no existe en tabla Profesor: {rut_clean}")
            return RedirectResponse(url="/", status_code=302)
        
        logging.info(f"Redirigiendo a menú profesor")
        return RedirectResponse(url="/menu_profesor", status_code=302)
    else:
        logging.warning(f"Rol desconocido: {rol_persona.RolId} para RUT: {rut_clean}")
        return RedirectResponse(url="/", status_code=302)

# ===== TIENDA / INVENTARIO =====
@app.get("/tienda", response_class=HTMLResponse)
def tienda(request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    items = db.query(Item).all()
    skin_activa = get_skin_activa(db, rut)

    return templates.TemplateResponse("tienda.html", {
        "request": request,
        "glims": est.Puntos or 0,
        "items": items,
        "skin_activa": skin_activa,
    })

@app.post("/comprar/{item_id}", response_class=RedirectResponse)
def comprar_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        return RedirectResponse(url="/tienda?err=est", status_code=302)

    it = db.query(Item).filter_by(idItem=item_id).first()
    if not it or it.Costo is None:
        return RedirectResponse(url="/tienda?err=item", status_code=302)

    glims = est.Puntos or 0
    if glims < it.Costo:
        return RedirectResponse(url="/tienda?err=saldo", status_code=302)

    est.Puntos = glims - it.Costo

    inv = db.query(Inventario).filter_by(EstudianteRUT=rut, ItemId=item_id).first()
    if inv:
        inv.Cantidad = (inv.Cantidad or 0) + 1
    else:
        inv = Inventario(EstudianteRUT=rut, ItemId=item_id, Cantidad=1)
        db.add(inv)

    db.commit()
    return RedirectResponse(url="/tienda?ok=1", status_code=302)

@app.get("/inventario", response_class=HTMLResponse)
def ver_inventario(request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    filas = (
        db.query(Inventario, Item)
        .join(Item, Inventario.ItemId == Item.idItem)
        .filter(Inventario.EstudianteRUT == rut)
        .all()
    )
    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    skin_activa = get_skin_activa(db, rut)

    return templates.TemplateResponse("inventario.html", {
        "request": request,
        "glims": est.Puntos or 0,
        "filas": filas,
        "skin_activa": skin_activa,
    })

@app.post("/aplicar_skin/{item_id}", response_class=RedirectResponse)
def aplicar_skin(item_id: int, request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    it = db.query(Item).filter_by(idItem=item_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    inv = db.query(Inventario).filter_by(EstudianteRUT=rut, ItemId=item_id).first()
    if not inv or (inv.Cantidad or 0) <= 0:
        return RedirectResponse(url="/inventario?err=no_posee", status_code=302)

    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Si la columna SkinActivaId no existe en la BD web, este set no hará efecto.
    # Para que funcione en producción, aplica el parche SQL que dejo abajo.
    if hasattr(est, "SkinActivaId"):
        est.SkinActivaId = item_id
        db.commit()

    return RedirectResponse(url="/inventario?ok=aplicada", status_code=302)

# # ---------------------- DASHBOARD (ÚNICO) ----------------------
# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard(request: Request, db: Session = Depends(get_db)):
#     rut = request.session.get("rut")
#     if not rut:
#         return RedirectResponse("/", status_code=302)

#     estudiante = (
#         db.query(Estudiante)
#         .options(joinedload(Estudiante.persona))
#         .filter_by(RUT=rut)
#         .first()
#     )
#     if not estudiante:
#         return RedirectResponse("/", status_code=302)

#     persona = estudiante.persona

#     # Asignatura base (si tu template muestra "Unidades de {{ lenguaje.Nombre }}")
#     lenguaje = db.query(Asignatura).filter_by(Nombre="Lenguaje y Comunicación").first()

#     # Unidades de esa asignatura
#     unidades = db.query(Unidad).filter_by(AsignaturaId=lenguaje.idAsignatura).all() if lenguaje else []

#     # Sesiones agrupadas por unidad
#     sesiones_por_unidad = {}
#     if lenguaje:
#         for s in (
#             db.query(Sesion)
#             .join(Unidad)
#             .filter(Unidad.AsignaturaId == lenguaje.idAsignatura)
#             .all()
#         ):
#             sesiones_por_unidad.setdefault(s.UnidadId, []).append(s)

#     # Progreso emocional
#     registros = db.query(RegistroEmocional).filter_by(EstudianteRUT=rut).all()
#     pre_sessions = {r.SesionId for r in registros if r.Tipo == TipoEmocionEnum.pre}
#     post_sessions = {r.SesionId for r in registros if r.Tipo == TipoEmocionEnum.post}

#     # Notas por sesión
#     desempenos = db.query(Desempeno).filter_by(EstudianteRUT=rut).all()
#     notas_por_sesion = {}
#     for d in desempenos:
#         test = db.query(Test).filter_by(idTest=d.TestId).first()
#         if test:
#             notas_por_sesion[test.SesionId] = d

#     ctx = {
#         "request": request,
#         "persona": persona,
#         "estudiante": estudiante,
#         "unidades": unidades,
#         "sesiones_por_unidad": sesiones_por_unidad,
#         "pre_sessions": pre_sessions,
#         "post_sessions": post_sessions,
#         "notas_por_sesion": notas_por_sesion,
#         **common_context(request, db)  # <-- glims + skin_activa para navbar
#     }
#     return templates.TemplateResponse("dashboard.html", ctx)

# ---------------------- DASHBOARD (Estudiante) ----------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    rut = request.session.get("rut")
    rol = request.session.get("rol")

    # Verifico sesión y rol
    if not rut or rol != "estudiante":
        return RedirectResponse("/", status_code=302)

    estudiante = (
        db.query(Estudiante)
        .options(joinedload(Estudiante.persona))
        .filter_by(RUT=rut)
        .first()
    )
    if not estudiante:
        return RedirectResponse("/", status_code=302)

    persona = estudiante.persona

    # Asignatura base
    lenguaje = db.query(Asignatura).filter_by(Nombre="Lenguaje y Comunicación").first()
    unidades = db.query(Unidad).filter_by(AsignaturaId=lenguaje.idAsignatura).all() if lenguaje else []

    sesiones_por_unidad = {}
    if lenguaje:
        for s in (
            db.query(Sesion)
            .join(Unidad)
            .filter(Unidad.AsignaturaId == lenguaje.idAsignatura)
            .all()
        ):
            sesiones_por_unidad.setdefault(s.UnidadId, []).append(s)

    registros = db.query(RegistroEmocional).filter_by(EstudianteRUT=rut).all()
    pre_sessions = {r.SesionId for r in registros if r.Tipo == TipoEmocionEnum.pre}
    post_sessions = {r.SesionId for r in registros if r.Tipo == TipoEmocionEnum.post}

    desempenos = db.query(Desempeno).filter_by(EstudianteRUT=rut).all()
    notas_por_sesion = {}
    for d in desempenos:
        test = db.query(Test).filter_by(idTest=d.TestId).first()
        if test:
            notas_por_sesion[test.SesionId] = d

    ctx = {
        "request": request,
        "persona": persona,
        "estudiante": estudiante,
        "unidades": unidades,
        "sesiones_por_unidad": sesiones_por_unidad,
        "pre_sessions": pre_sessions,
        "post_sessions": post_sessions,
        "notas_por_sesion": notas_por_sesion,
        **common_context(request, db)
    }
    return templates.TemplateResponse("dashboard.html", ctx)
 

# ---------------------- MENÚ PROFESOR ----------------------
@app.get("/menu_profesor", response_class=HTMLResponse)
def menu_profesor(request: Request, db: Session = Depends(get_db)):
    from app import common_context
    rut = request.session.get("rut")
    rol = request.session.get("rol")

    

    # Verifico sesión y rol
    if not rut or rol != "profesor":
        return RedirectResponse("/", status_code=302)

    # Traigo info básica del profesor para mostrar en template (si es necesario)
    profesor = db.query(Profesor).options(joinedload(Profesor.persona)).filter_by(RUT=rut).first()
    if not profesor:
        return RedirectResponse("/", status_code=302)

    persona = profesor.persona
    ctx = {
        "request": request,
        "profesor": profesor,
        "persona": persona,
        **common_context(request, db)
    }
    return templates.TemplateResponse("menu_profesor.html", ctx)


# ---------------------- ESTUDIO ----------------------
@app.get("/estudio", response_class=HTMLResponse)
def estudio_material(request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]
    est = get_estudiante(db, rut)
    materiales = (
        db.query(Material)
        .filter_by(CursoId=est.CursoId)
        .order_by(Material.SubidoEn.desc())
        .all()
    )
    return templates.TemplateResponse("estudio_material.html", {
        "request": request,
        "materiales": materiales,
        **common_context(request, db)
    })

@app.get("/download/{rel_path:path}")
def force_download(rel_path: str):
    file_path = _safe_join_uploads(rel_path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"

    return FileResponse(
        path=str(file_path),
        media_type=mime,
        filename=file_path.name,
        headers={"Content-Disposition": f'attachment; filename="{file_path.name}"'}
    )

# ---------------------- DESAFÍO (flujo Web) ----------------------
@app.get("/desafio/asignaturas", response_class=HTMLResponse)
def desafio_asignaturas(request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    asignaturas = db.query(Asignatura).all()
    return templates.TemplateResponse("asignaturas.html", {
        "request": request,
        "asignaturas": asignaturas,
        **common_context(request, db)
    })

@app.get("/desafio/unidades/{asig_id}", response_class=HTMLResponse)
def desafio_unidades(asig_id: int, request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    asig = db.query(Asignatura).get(asig_id)
    if not asig:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    unidades = (
        db.query(Unidad)
        .filter_by(AsignaturaId=asig_id)
        .order_by(Unidad.Numero.asc())
        .all()
    )
    unidades_estado = [(u, is_unit_unlocked(db, rut, u)) for u in unidades]

    return templates.TemplateResponse("unidades.html", {
        "request": request,
        "asignatura": asig,
        "unidades_estado": unidades_estado,
        **common_context(request, db)
    })

@app.get("/desafio/sesiones/{unidad_id}", response_class=HTMLResponse)
def desafio_sesiones(unidad_id: int, request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    unidad = db.query(Unidad).get(unidad_id)
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    if not is_unit_unlocked(db, rut, unidad):
        return RedirectResponse(url=f"/desafio/unidades/{unidad.AsignaturaId}?locked=1", status_code=302)

    sesiones = db.query(Sesion).filter_by(UnidadId=unidad_id).all()
    ses_estado = [(s, is_session_completed(db, rut, s.idSesion)) for s in sesiones]

    return templates.TemplateResponse("sesiones.html", {
        "request": request,
        "unidad": unidad,
        "sesiones_estado": ses_estado,
        **common_context(request, db)
    })

# ---------------------- PRE / TEST (flujo Web) ----------------------
@app.get("/desafio/precheck/{sesion_id}", response_class=HTMLResponse)
def precheck_form(sesion_id: int, request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    s = db.query(Sesion).get(sesion_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return templates.TemplateResponse("pre_check.html", {
        "request": request,
        "sesion_id": sesion_id,
        **common_context(request, db)
    })

@app.post("/desafio/precheck/{sesion_id}", response_class=RedirectResponse)
def precheck_submit(sesion_id: int, request: Request, escala: int = Form(...), db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]
    reg = RegistroEmocional(
        EstudianteRUT=rut, EmocionId=1, Tipo=TipoEmocionEnum.pre,
        Escala=escala, Fecha=datetime.now(), SesionId=sesion_id
    )
    db.add(reg); db.commit()
    request.session.pop(f"answers_{sesion_id}", None)
    return RedirectResponse(url=f"/desafio/test/{sesion_id}?i=0", status_code=302)

@app.get("/desafio/test/{sesion_id}", response_class=HTMLResponse)
def test_step(
    sesion_id: int,
    i: int = 0,
    request: Request = None,
    db: Session = Depends(get_db),
):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)

    test = get_test_by_sesion(db, sesion_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")

    items = get_preguntas_de_test(db, test.idTest)
    if i < 0 or i >= len(items):
        return RedirectResponse(url=f"/desafio/test/finish/{sesion_id}", status_code=302)

    item = items[i]

    seccion_id = None
    if item.get("tipo") == "alternativa":
        pal = db.query(PAlternativas).filter_by(idPregunta=item["pregunta_id"]).first()
        seccion_id = pal.SeccionPId if pal else None
    else:
        pd = db.query(PDesarrollo).filter_by(idPregunta=item["pregunta_id"]).first()
        seccion_id = pd.SeccionPId if pd else None

    pasaje_img = _imagen_seccion_base64(db, seccion_id)
    sec = db.query(SeccionP).filter_by(idSeccionP=seccion_id).first() if seccion_id else None
    pasaje_desc = sec.Descripcion if sec else None

    answers = request.session.get(f"answers_{sesion_id}", {})
    respuesta_actual = answers.get(str(item["pregunta_id"]), "")

    return templates.TemplateResponse(
        "test_step.html",
        {
            "request": request,
            "sesion_id": sesion_id,
            "index": i,
            "total": len(items),
            "item": item,
            "respuesta_actual": respuesta_actual,
            "pasaje_img": pasaje_img,
            "pasaje_desc": pasaje_desc,
            **common_context(request, db),
        },
    )

@app.post("/desafio/test/{sesion_id}", response_class=RedirectResponse)
def test_step_submit(
    sesion_id: int,
    i: int = Form(...),
    pregunta_id: int = Form(...),
    respuesta: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    key = f"answers_{sesion_id}"
    answers = request.session.get(key, {})
    answers[str(pregunta_id)] = respuesta
    request.session[key] = answers
    return RedirectResponse(url=f"/desafio/test/{sesion_id}?i={int(i)+1}", status_code=302)

@app.get("/desafio/test/finish/{sesion_id}", response_class=RedirectResponse)
def test_finish(sesion_id: int, request: Request, db: Session = Depends(get_db)):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]

    test = get_test_by_sesion(db, sesion_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test no encontrado")

    items = get_preguntas_de_test(db, test.idTest)
    answers = request.session.get(f"answers_{sesion_id}", {})
    score = compute_score(items, answers)

    dep = db.query(Desempeno).filter_by(EstudianteRUT=rut, TestId=test.idTest).first()
    est = db.query(Estudiante).filter_by(RUT=rut).first()
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    glims_add = 0
    if dep:
        prev = dep.NotaTest or 0
        if score > prev:
            glims_add = glims_delta_from_scores(score, prev)
            dep.NotaTest = score
            dep.FechaEvaluacion = date.today()
            est.Puntos = (est.Puntos or 0) + glims_add
    else:
        glims_add = glims_delta_from_scores(score, 0)
        dep = Desempeno(
            EstudianteRUT=rut,
            TestId=test.idTest,
            NotaTest=score,
            FechaEvaluacion=date.today()
        )
        db.add(dep)
        est.Puntos = (est.Puntos or 0) + glims_add

    db.commit()
    request.session.pop(f"answers_{sesion_id}", None)

    return RedirectResponse(
        url=f"/desafio/postcheck/{sesion_id}?score={score}&glims={glims_add}",
        status_code=302
    )

# ---------------------- POST-CHECK ----------------------
@app.get("/desafio/postcheck/{sesion_id}", response_class=HTMLResponse)
def postcheck_form(
    sesion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    score: int | None = Query(default=None),
    glims: int | None = Query(default=None),
):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)

    s = db.query(Sesion).get(sesion_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    return templates.TemplateResponse("post_check.html", {
        "request": request,
        "sesion_id": sesion_id,
        "score": score,
        "glims_earned": glims,
        **common_context(request, db)
    })

@app.post("/desafio/postcheck/{sesion_id}", response_class=RedirectResponse)
def postcheck_submit(
    sesion_id: int,
    request: Request,
    escala: int = Form(...),
    contexto: str = Form(None),
    db: Session = Depends(get_db)
):
    if "rut" not in request.session:
        return RedirectResponse("/", status_code=302)
    rut = request.session["rut"]
    reg = RegistroEmocional(
        EstudianteRUT=rut, EmocionId=2, Tipo=TipoEmocionEnum.post,
        Escala=escala, Contexto=contexto, Fecha=datetime.now(), SesionId=sesion_id
    )
    db.add(reg); db.commit()
    unidad_id = db.query(Sesion).get(sesion_id).UnidadId
    return RedirectResponse(url=f"/desafio/sesiones/{unidad_id}?ok=1", status_code=302)

# ---------------------- LOGOUT ----------------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# ---------------------- ENDPOINTS MÓVILES (ligeros) ----------------------
@app.get("/asignaturas/{asig_id}/unidades")
def unidades_por_asignatura(asig_id: int, db: Session = Depends(get_db)):
    return db.query(Unidad).filter(Unidad.asignatura_id == asig_id).all()

@app.get("/unidades/{unidad_id}/sesiones")
def sesiones_por_unidad(unidad_id: int, db: Session = Depends(get_db)):
    q = (
        db.query(Sesion)
        .filter(Sesion.unidad_id == unidad_id)
        .order_by(Sesion.id)
        .all()
    )
    return [
        {"id": s.id, "bitacora": s.bitacora, "objetivo": s.objetivo_aprendizaje}
        for s in q
    ]

@app.get("/sesiones/{sesion_id}/detalle")
def sesion_detalle(sesion_id: int, db: Session = Depends(get_db)):
    sesion = (
        db.query(Sesion)
        .options(joinedload(Sesion.tests).joinedload(Test.preguntas))
        .filter(Sesion.id == sesion_id)
        .first()
    )
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    return {
        "id": sesion.id,
        "bitacora": sesion.bitacora,
        "objetivo": sesion.objetivo_aprendizaje,
        "tests": [
            {
                "id": t.id,
                "puntaje": t.puntaje,
                "descripcion": t.descripcion,
                "preguntas": [
                    {
                        "id": p.id,
                        "tipo": p.tipo.value,
                        "puntaje": p.puntaje,
                        "enunciado": (
                            p.alternativas.enunciado if p.tipo == TipoPreguntaEnum.Alternativa
                            else (p.desarrollo.enunciado if p.desarrollo else "")
                        ),
                        "alternativas": (
                            {
                                "A": p.alternativas.p_a,
                                "B": p.alternativas.p_b,
                                "C": p.alternativas.p_c,
                                "D": p.alternativas.p_d,
                                "correcta": p.alternativas.correcta,
                            } if p.alternativas else None
                        ) if p.tipo == TipoPreguntaEnum.Alternativa else None,
                    }
                    for p in t.preguntas
                ],
            }
            for t in sesion.tests
        ],
    }



# ---------------------- CHATBOT ----------------------
# Modelo de entrada
class ChatMessage(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Servidor corriendo 🚀"}


