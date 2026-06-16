from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from services.chatbot_service import get_chatbot_response
from models import RegistroIA, Estudiante
from database import get_db  # función que devuelve la sesión de DB
# from app import common_context  # trae glims, skin, usuario_rut

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
templates = Jinja2Templates(directory="templates")


# Modelo para el mensaje del usuario
class ChatRequest(BaseModel):
    message: str


# ----------------------------------------------------------
# GET: Renderizar página del chatbot con glims, skin y rut
# ----------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def chat_page(request: Request, db: Session = Depends(get_db)):
    """
    Renderiza la página del chatbot.
    Obtiene el RUT del usuario desde la sesión activa.
    """
    rut_estudiante = request.session.get("rut")

    # Si el usuario no ha iniciado sesión → redirigir a login
    if not rut_estudiante:
        return RedirectResponse("/", status_code=302)

    estudiante = db.query(Estudiante).filter_by(RUT=rut_estudiante).first()
    if not estudiante:
        return RedirectResponse("/", status_code=302)

    # 🔹 Se pasa common_context para mostrar glims y skin activa
    return templates.TemplateResponse(
        "chatbot.html",
        {
            "request": request,
            "estudiante": estudiante,
            "rut_estudiante": rut_estudiante,
            # **common_context(request, db)
        },
    )


# ----------------------------------------------------------
# POST: Enviar mensaje y registrar conversación
# ----------------------------------------------------------
@router.post("/", response_class=JSONResponse)
def chat_post(request: Request, data: ChatRequest, db: Session = Depends(get_db)):
    """
    Guarda tanto el mensaje del estudiante como la respuesta de Aurora.
    """
    rut_estudiante = request.session.get("rut")

    if not rut_estudiante:
        return {"error": "Usuario no autenticado"}

    # Obtener respuesta de Aurora (ChatGPT / servicio local)
    respuesta = get_chatbot_response(data.message)

    # Guardar mensaje del estudiante
    mensaje_usuario = RegistroIA(
        rut_estudiante=rut_estudiante,
        sesion_id=1,  
        remitente="estudiante",
        mensaje=data.message,
        fecha_hora=datetime.now()
    )
    db.add(mensaje_usuario)

    # Guardar respuesta de Aurora
    mensaje_aurora = RegistroIA(
        rut_estudiante=rut_estudiante,
        sesion_id=1,
        remitente="aurora",
        mensaje=respuesta,
        fecha_hora=datetime.now()
    )
    db.add(mensaje_aurora)

    db.commit()

    return {
        "usuario": data.message,
        "aurora": respuesta
    }


# ----------------------------------------------------------
# GET: Historial del chat (para mostrar al cargar la página)
# ----------------------------------------------------------
@router.get("/historial", response_class=JSONResponse)
def historial_chat(request: Request, db: Session = Depends(get_db)):
    """
    Retorna el historial completo de conversación del usuario logueado.
    """
    rut_estudiante = request.session.get("rut")

    if not rut_estudiante:
        return {"error": "Usuario no autenticado"}

    registros = (
        db.query(RegistroIA)
        .filter_by(rut_estudiante=rut_estudiante)
        .order_by(RegistroIA.fecha_hora.asc())  
        .all()
    )

    return [
        {
            "remitente": r.remitente,
            "mensaje": r.mensaje,
            "fecha": r.fecha_hora.strftime("%Y-%m-%d %H:%M")
        }
        for r in registros
    ]
