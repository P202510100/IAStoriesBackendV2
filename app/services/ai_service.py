import json
import requests
import base64
import time

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
FREEPIK_API_KEY = settings.FREEPIK_API_KEY
FREEPIK_URL = "https://api.freepik.com/v1/ai/mystic"

def generar_historia_y_preguntas(nombre: str, edad: int, elementos: str, grado: str, topic: str):

    story_metadata = {
        "edad": edad,
        "grado": grado,
        "elementos_especiales": elementos,
        "topic": topic
    }


    prompt = f"""
    ### INSTRUCCIONES ###
    Usa los siguientes datos:
        - Protagonista:{nombre}
        - Edad del protagonista: {edad}
        - Elementos especiales que deben aparecer en la historia: {elementos}
        - Nivel escolar actual: {grado}
        - Tema principal de la historia: {topic}

    ### REQUISITOS ###
    1. Genera una historia con la siguiente estructura detallada:
        - INTRODUCCIÓN (200-250 palabras): Presentar a {nombre}, su personalidad y mundo
        - PROBLEMA/DESAFÍO (100-200 palabras): Conflicto específico que debe resolver
        - DESARROLLO (200-300 palabras): Cómo {nombre} enfrenta el desafío con detalles
        - CLÍMAX (200-250 palabras): Momento crucial de la resolución
        - RESOLUCIÓN Y APRENDIZAJE (200-250 palabras): Solución exitosa y lección educativa
    2. Incluye al protagonista y los elementos especiales.
    3. Devuelve también un conjunto de 6 preguntas de comprensión lectora.
       - Obligatoriamente tiene que tener 2 preguntas inferenciales.
       - Obligatoriamente tiene que tener 2 preguntas juicio crítico.
       - Obligatoriamente tiene que tener 2 preguntas creativas.
       - Obligatoriamente cada pregunta debe tener 4 alternativas.
       - Indica la respuesta correcta con el índice (0, 1, 2 o 3).
    4. Todo el contenido/content debe contener mínimo de palabras son 2000 palabras aprox.
    5. Incluir diálogos realistas.
    6. Detalles específicos y únicos de esta historia.
    7. Mencionar elementos del tema {topic}.
    8. Lenguaje apropiado para {edad} años.
    9. Historia ÚNICA que genere preguntas específicas.
    10. Sin violencia, final positivo.
    11. Devuelve TODO en un JSON válido con esta estructura:
    12. En el campo content no colocar las palabras INTRODUCCIÓN, PROBLEMA/DESAFIO, DESARROLLO, CLÍMAX, RESOLUCIÓN Y APRENDIZAJE, porque es innecesario. Solo dar el contenido puro.
    
    {{
      "title": "...",
      "content": "...",
      "characters": ["..."],
      "story_metadata": {json.dumps(story_metadata, ensure_ascii=False)},
      "questions": [
        {{
          "question": "",
          "options": ["A", "B", "C", "D"],
          "answer": "A"
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en Educación, tanto para niños, jovenes y adultos. Debes generar historias educativas para enriquecer y mejorar la comprensión lectora en niños."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=2000
    )

    raw_output = response.choices[0].message.content

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(f"Error al parsear respuesta IA: {raw_output}")


def generar_historia_preguntas_imagen(nombre: str, edad: int, elementos: str, grado: str, topic: str):
    historia = generar_historia_y_preguntas(nombre, edad, elementos, grado, topic)

    prompt_img = (
        f"Ilustración infantil, estilo caricatura, alegre y colorida. "
        f"Tema: {topic}. Personaje principal: {nombre}, {edad} años. "
        f"Elementos a incluir: {elementos}. "
        f"Debe reflejar el ambiente y la esencia de la historia."
    )

    headers = {
        "x-freepik-api-key": f"{FREEPIK_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(FREEPIK_URL, headers=headers, json={"prompt": prompt_img})

    if response.status_code != 200:
        historia["image_b64"] = None
        return historia

    task_id = response.json()["data"]["task_id"]

    image_url = None

    for _ in range(10):
        status_resp = requests.get(f"{FREEPIK_URL}/{task_id}", headers=headers)
        status_data = status_resp.json().get("data", {})

        if status_data.get("status") == "COMPLETED" and status_data.get("generated"):
            image_url = status_data["generated"][0]
            break
        time.sleep(2)

    if not image_url:
        historia["image_b64"] = None
        return historia

    img_resp = requests.get(image_url)
    if img_resp.status_code == 200:
        historia["image_b64"] = base64.b64encode(img_resp.content).decode("utf-8")
    else:
        historia["image_b64"] = None

    return historia
