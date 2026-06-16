📦 Aurora Backend - API REST

Este proyecto es el backend en FastAPI que conecta a la base de datos MySQL cargada en cPanel. Aquí encontrarás toda la información necesaria para que el equipo frontend consuma los endpoints.

🚀 Endpoints principales

✅ CRUD por entidad

✅ Autenticación básica

POST /register → registrar nuevo usuario (crea Persona + Usuario)

Params: rut, nombres, apellidop, apellidom, comuna_id, colegio_id

POST /login → validar que el usuario existe en Usuario

Params: rut, colegio_id

⚠ Nota: actualmente no maneja contraseñas porque no hay columna password en la base.

✅ Swagger UI (documentación interactiva)

Accede a:

http://localhost:8000/docs

Aquí el equipo frontend puede explorar los endpoints, probarlos, y ver sus formatos.

🔑 Configuración CORS

El backend tiene habilitado CORS para permitir peticiones desde cualquier dominio.

Si quieres restringirlo (más seguro), modifica en main.py:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # aquí puedes poner https://mi-frontend.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

📦 Estructura del proyecto

/AuroraBackendWeb/
├── app.py (entrada principal)
├── models.py (modelos SQLAlchemy)
├── database.py (conexión MySQL)
├── routers/ (opcional si modularizas)
├── statics/
├── templates/
├── requirements.txt (dependencias)
└── venv (entorno virtual)


Base de datos configurada en .env (Aqui estan las credenciales)


⚙ Requisitos para correr localmente

Python 3.10+
Correr Requirements.txt
FastAPI, SQLAlchemy, PyMySQL, Uvicorn, python-dotenv



🚀 Cómo correr localmente

uvicorn main:app --reload

Esto levanta el backend en:

http://localhost:8000