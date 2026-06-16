import os
from dotenv import load_dotenv

# Cargar .env con la api
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()
