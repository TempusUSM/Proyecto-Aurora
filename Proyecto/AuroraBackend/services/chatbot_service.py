from openai import OpenAI
from core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_chatbot_response(message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres Aurora, una asistente educativa amable."},
                {"role": "user", "content": message}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error en get_chatbot_response:", e)
        return "Error en la respuesta."

def analyze_emotion(scale: int, comment: str) -> str:
    """
    Envía la escala y comentario a la API de OpenAI para generar un análisis.
    """
    prompt = f"""
    El estudiante se calificó con una emoción de {scale} en una escala de 1 a 5,
    donde 1 es muy mal y 5 es muy bien.
    Comentario adicional: "{comment}"

    Genera un breve análisis educativo y empático de cómo se siente.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres Aurora, una asistente educativa empática que analiza emociones de estudiantes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()