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


def generar_historia_y_preguntas_v2(nombre: str, edad: int, elementos: str, grado: str, topic: str):
    story_metadata = {
        "edad": edad,
        "grado": grado,
        "elementos_especiales": elementos,
        "topic": topic
    }

    prompt = f"""
    Eres un pedagogo especializado en desarrollo de comprensión lectora con maestría en literatura infantil y didáctica de la lengua.

    MARCO PEDAGÓGICO:
    Trabajas bajo los principios de:
    - Taxonomía de Bloom (análisis, evaluación, creación)
    - Niveles de comprensión lectora: literal, inferencial, crítico
    - Desarrollo cognitivo según edad del estudiante
    - Escritura creativa con propósito educativo

    DATOS DEL ESTUDIANTE:
    - Protagonista: {nombre}
    - Edad: {edad} años
    - Nivel: {grado}
    - Tema: {topic}
    - Elementos narrativos: {elementos}

    COHERENCIA NARRATIVA OBLIGATORIA:
    Si {nombre} es un personaje conocido (Spider-Man, Elsa, Harry Potter):
    - Mantén características canónicas: habilidades, personalidad, contexto
    - Respeta su universo narrativo original
    - No inventes poderes o características inexistentes

    Si {elementos} incluyen objetos/conceptos conocidos:
    - Respeta su naturaleza y función
    - Intégralos lógicamente en la trama

    ESTRUCTURA NARRATIVA (MÍNIMO 650 PALABRAS):

    **ACTO I - PRESENTACIÓN (150-200 palabras)**
    Establece:
    - Protagonista con profundidad psicológica (miedos, deseos, valores)
    - Contexto sociocultural específico (no genérico)
    - Rutina que será interrumpida (mostrar normalidad antes del conflicto)
    - Gancho narrativo que genere curiosidad

    Técnicas literarias requeridas:
    - Descripción sensorial (3+ sentidos)
    - "Show, don't tell" (mostrar emociones con acciones, no nombrarlas)
    - Diálogo natural que revele personalidad

    **ACTO II - CONFLICTO Y DESARROLLO (300-350 palabras)**
    Presenta un dilema que requiera:
    - Decisión ética con consecuencias reales
    - Conflicto interno (deseo vs deber, miedo vs valentía)
    - Obstáculos progresivos (no un solo problema, sino escalada)
    - Integración natural de {elementos}

    El protagonista debe:
    - Dudar, equivocarse, aprender
    - Mostrar crecimiento emocional
    - Enfrentar consecuencias de sus decisiones

    Incluye:
    - Mínimo 3 diálogos significativos con otros personajes
    - Descripciones que avancen la trama (no decorativas)
    - Conectores causales explícitos (por lo tanto, debido a, como resultado)

    **ACTO III - CLÍMAX (100-120 palabras)**
    Momento de máxima tensión donde:
    - {nombre} aplica lo aprendido
    - La decisión tiene peso moral real
    - Las consecuencias son visibles inmediatamente

    **ACTO IV - RESOLUCIÓN (80-100 palabras)**
    Cierre que:
    - Muestre cambio en el protagonista (comparar con inicio)
    - Lección implícita (no moraleja explícita tipo "y aprendió que...")
    - Conexión emocional con el lector
    - Reflexión del protagonista sobre su transformación

    CALIDAD LITERARIA OBLIGATORIA:

    Vocabulario enriquecido apropiado para {grado}:
    - Edad 5-7: adjetivos descriptivos, verbos de acción específicos
    - Edad 8-10: sinónimos variados, vocabulario emocional complejo
    - Edad 11-15: lenguaje figurado, metáforas apropiadas

    Estructura de oraciones:
    - 60% simples (sujeto-verbo-predicado claro)
    - 30% compuestas (coordinadas con conectores)
    - 10% complejas (subordinadas apropiadas a la edad)

    Recursos literarios:
    - Personificación moderada
    - Comparaciones que clarifiquen (no que compliquen)
    - Onomatopeyas en momentos de acción
    - Repetición intencional para énfasis

    Diálogos auténticos:
    - Cada personaje con voz distintiva
    - Interrupciones y pausas naturales
    - Subtext (lo no dicho es tan importante como lo dicho)

    PROHIBICIONES ABSOLUTAS:
    - Resoluciones mágicas sin esfuerzo
    - "Y vivieron felices para siempre" genérico
    - Adultos que resuelven todo
    - Violencia gráfica o temas inapropiados
    - Estereotipos de género, raza o clase social
    - Moraleja explícita al final

    PREGUNTAS DE COMPRENSIÓN LECTORA (6 OBLIGATORIAS):

    **2 PREGUNTAS INFERENCIALES (orden: 1 y 2)**
    Requieren:
    - Deducir información NO explícita en el texto
    - Relacionar causa-efecto entre secciones distintas
    - Interpretar motivaciones de personajes
    - Conectar acciones con consecuencias

    Estructura de opciones incorrectas:
    - Plausibles pero sin evidencia textual
    - Contradicen sutilmente el texto
    - Son literales cuando se requiere inferencia

    Ejemplo de calidad:
    Pregunta: "¿Por qué {nombre} decidió ayudar al antagonista a pesar del riesgo?"
    A) Porque era valiente (INCORRECTO: muy literal)
    B) Porque comprendió que todos merecen una segunda oportunidad (CORRECTO: requiere inferir el cambio de perspectiva)
    C) Porque no tenía otra opción (INCORRECTO: contradice el texto)
    D) Porque quería impresionar a otros (INCORRECTO: plausible pero sin evidencia)

    **2 PREGUNTAS DE JUICIO CRÍTICO (orden: 3 y 4)**
    Requieren:
    - Evaluar decisiones de personajes
    - Analizar dilemas éticos
    - Considerar perspectivas múltiples
    - Argumentar posiciones morales

    Las opciones TODAS deben tener mérito argumentativo:
    - Evitar respuestas obviamente correctas/incorrectas
    - Cada opción representa una postura ética defendible
    - La "correcta" debe ser la más fundamentada en el texto

    Ejemplo de calidad:
    Pregunta: "¿Fue correcto que {nombre} mintiera para proteger a su amigo?"
    A) Sí, porque la amistad está por encima de todo (INCORRECTO: absoluto, no considera contexto)
    B) Sí, porque evitó un daño mayor y asumió las consecuencias (CORRECTO: ponderado, contextual)
    C) No, porque mentir siempre está mal (INCORRECTO: muy rígido)
    D) No, porque debió buscar otra solución (DEFENDIBLE: pero el texto muestra que no había otra opción inmediata)

    **2 PREGUNTAS CREATIVAS (orden: 5 y 6)**
    Requieren:
    - Proyectar el contenido del texto hacia nuevas situaciones.
    - Imaginar finales alternativos, soluciones o extensiones del conflicto.
    - Aplicar los valores, aprendizajes o ideas del texto en contextos distintos.
    - Transformar la información textual en propuestas originales pero coherentes.
    
    Estructura de opciones incorrectas:
    - Fantásticas o absurdas sin relación con el contexto del texto.
    - Repetitivas o meramente literales (sin transformación).
    - Incoherentes con la personalidad o motivaciones de los personajes.

    Estructura de la opción correcta:
    - Creativa pero verosímil.
    - Respeta el tono, los valores o la lógica interna del texto.
    - Muestra comprensión profunda del conflicto y lo reinterpreta con originalidad.
    
    Ejemplo de calidad:
    Pregunta: “Si {nombre} tuviera la oportunidad de cambiar una sola decisión tomada en la historia, ¿cuál sería y por qué?”
    A) No cambiaría nada, porque todo terminó bien. (INCORRECTO: literal, sin pensamiento creativo)
    B) Evitaría conocer al antagonista para no sufrir. (INCORRECTO: elimina el conflicto principal, poco verosímil)
    C) Decidiría confiar antes en sus amigos para resolver el problema juntos. (CORRECTO: propuesta nueva, coherente con la evolución del personaje)
    D) Desaparecería del mundo para que nadie sufra. (INCORRECTO: fantasiosa y desconectada del tono del texto)

    FORMATO JSON DE SALIDA:
    
    {{
      "title": "Título evocativo (no obvio ni descriptivo)",
      "content": "Historia completa SIN etiquetas ni marcadores de sección. Mínimo 650 palabras. Texto fluido con párrafos bien delimitados",
      "characters": ["{nombre}", "personaje_2", "personaje_3"],
      "story_metadata": {json.dumps(story_metadata, ensure_ascii=False)},
      "questions": [
        {{
          "question": "Pregunta inferencial 1",
          "options": ["A", "B", "C", "D"],
          "answer": 1,
          "type": "inferencial"
        }},
        {{
          "question": "Pregunta inferencial 2",
          "options": ["A", "B", "C", "D"],
          "answer": 2,
          "type": "inferencial"
        }},
        {{
          "question": "Pregunta juicio crítico 1",
          "options": ["A", "B", "C", "D"],
          "answer": 1,
          "type": "juicio_critico"
        }},
        {{
          "question": "Pregunta juicio crítico 2",
          "options": ["A", "B", "C", "D"],
          "answer": 3,
          "type": "juicio_critico"
        }},
        {{
          "question": "Pregunta creativa 1",
          "options": ["A", "B", "C", "D"],
          "answer": 0,
          "type": "creativa"
        }},
        {{
          "question": "Pregunta creativa 2",
          "options": ["A", "B", "C", "D"],
          "answer": 1,
          "type": "creativa"
        }}
      ]
    }}

    CRITERIOS DE ÉXITO:
    1. Historia con arco transformador visible (protagonista diferente al final).
    2. Conflicto con peso emocional real.
    3. Diálogos que revelan carácter.
    4. Vocabulario desafiante pero accesible.
    5. Preguntas que requieren pensar, no recordar.
    6. Mínimo 650 palabras en "content".

    Ahora, genera la historia educativa/profesional.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Eres un pedagogo especializado en literatura infantil y desarrollo de comprensión lectora. Generas historias educativas de alta calidad."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=4000
    )

    raw_output = response.choices[0].message.content
    try:
        result = json.loads(raw_output)

        # ✅ VALIDACIÓN Y CORRECCIÓN de tipos de preguntas
        if "questions" in result and isinstance(result["questions"], list):
            # Orden esperado: 2 inferenciales, 2 juicio crítico, 2 creativas
            tipos_correctos = [
                "inferencial",
                "inferencial",
                "juicio_critico",
                "juicio_critico",
                "creativa",
                "creativa"
            ]

            # Asignar el tipo correcto a cada pregunta según su posición
            for i, question in enumerate(result["questions"]):
                if i < len(tipos_correctos):
                    # Forzar el tipo correcto según la posición
                    question["type"] = tipos_correctos[i]
                else:
                    # Si hay más de 6 preguntas, por defecto inferencial
                    question["type"] = "inferencial"

        return result

    except json.JSONDecodeError:
        raise ValueError(f"Error al parsear respuesta IA: {raw_output}")

def generar_historia_preguntas_imagen(nombre: str, edad: int, elementos: str, grado: str, topic: str):
    historia = generar_historia_y_preguntas_v2(nombre, edad, elementos, grado, topic)

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
