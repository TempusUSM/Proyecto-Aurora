# routers/dashboard_profesor/dashboard_emocional.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Profesor, Curso, Estudiante, Desempeno, RegistroEmocional, RegistroIA
from fastapi.templating import Jinja2Templates
from datetime import datetime
from openai import OpenAI
import os

# Configuración base
templates = Jinja2Templates(directory="templates")
router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Función auxiliar para resumen con IA
def resumen_emocional(estudiante_rut, registros):
    texto = "Analiza los siguientes registros emocionales del estudiante:\n"
    for r in registros:
        texto += f"- Fecha: {r.Fecha}, Escala: {r.Escala}, Contexto: {r.Contexto or 'N/A'}, Resumen: {r.Resumen or 'N/A'}\n"
    prompt = f"{texto}\nHaz un resumen de cómo se siente el estudiante y su progreso emocional."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Ruta principal del dashboard emocional
@router.get("/dashboard_emocional", response_class=HTMLResponse)
@router.post("/dashboard_emocional", response_class=HTMLResponse)
def dashboard_emocional(
    request: Request,
    curso: str = Form(default=None),
    estudiante: str = Form(default=None),
    db: Session = Depends(get_db)
):
    profesor_rut = "12345678-9"  

    #  Cargar cursos del profesor
    cursos = db.query(Curso).filter(Curso.ProfesorJefeRUT == profesor_rut).all()

    # Cargar estudiantes según curso
    estudiantes_query = db.query(Estudiante)
    if curso:
        estudiantes_query = estudiantes_query.filter(Estudiante.CursoId == int(curso))
    estudiantes = estudiantes_query.all()

    # Cargar desempeño y registros emocionales
    desempenos_query = db.query(Desempeno).join(Estudiante)
    if estudiante:
        desempenos_query = desempenos_query.filter(Desempeno.EstudianteRUT == estudiante)
    elif curso:
        desempenos_query = desempenos_query.filter(Estudiante.CursoId == int(curso))
    desempenos = desempenos_query.all()

    registros_emocionales_query = db.query(RegistroEmocional).join(Estudiante)
    if estudiante:
        registros_emocionales_query = registros_emocionales_query.filter(RegistroEmocional.EstudianteRUT == estudiante)
    elif curso:
        registros_emocionales_query = registros_emocionales_query.filter(Estudiante.CursoId == int(curso))
    registros_emocionales = registros_emocionales_query.all()

    # Extraer fechas y emociones para gráficas
    fechas = [
        r.Fecha.strftime("%d-%m-%Y") if isinstance(r.Fecha, datetime) else str(r.Fecha)
        for r in registros_emocionales
    ]
    emociones = [r.Escala for r in registros_emocionales]
    comentarios = [r.Contexto or "" for r in registros_emocionales]

    # Resumen generado por IA (solo si hay un estudiante específico)
    resumen = None
    if estudiante and registros_emocionales:
        resumen = resumen_emocional(estudiante, registros_emocionales)



    # 6️⃣ Renderizar el template con toda la información
    return templates.TemplateResponse(
        "dashboard_emocional.html",
        {
            "request": request,
            "cursos": cursos,
            "estudiantes": estudiantes,
            "selected_curso": curso,
            "selected_estudiante": estudiante,
            "desempenos": desempenos,
            "registros_emocionales": registros_emocionales,
            "fechas": fechas,
            "emociones": emociones,
            "comentarios": comentarios,
            "resumen": resumen,
        },
    )

