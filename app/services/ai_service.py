import json

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generar_historia_y_preguntas(nombre: str, edad: int, elementos: str, grado: str, topic: str):

    story_metadata = {
        "edad": edad,
        "grado": grado,
        "elementos_especiales": elementos,
        "topic": topic
    }


    prompt = f"""
    Usa los siguientes datos:
        - Protagonista:{nombre}
        - Edad del protagonista: {edad}
        - Elementos especiales que deben aparecer en la historia: {elementos}
        - Nivel escolar actual: {grado}
        - Tema principal de la historia: {topic}

    Requisitos:
    1. Genera una historia con la siguiente estructura detallada:
        - INTRODUCCIÓN (100-150 palabras): Presentar a {nombre}, su personalidad y mundo
        - PROBLEMA/DESAFÍO (100-200 palabras): Conflicto específico que debe resolver
        - DESARROLLO (100-200 palabras): Cómo {nombre} enfrenta el desafío con detalles
        - CLÍMAX (100-150 palabras): Momento crucial de la resolución
        - RESOLUCIÓN Y APRENDIZAJE (100-150 palabras): Solución exitosa y lección educativa
    2. Incluye al protagonista y los elementos especiales.
    3. Devuelve también un conjunto de 6 preguntas de comprensión lectora.
       - Obligatoriamente cada pregunta debe tener 4 alternativas.
       - Indica la respuesta correcta con el índice (0, 1 o 2).
    4. Todo el contenido/content debe contener mínimo de palabras son 500 palabras (contar al final).
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
          "options": ["A", "B", "C"],
          "answer": "A
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
