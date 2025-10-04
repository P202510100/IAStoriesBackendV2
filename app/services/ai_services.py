import os
import json
from typing import Dict, List, Optional
from openai import OpenAI




class AIConfig:
    """Configuración centralizada de servicios de IA"""
    
    OPENAI_API_KEY = "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"
    OPENAI_MODEL = "gpt-3.5-turbo"
    IMAGE_MODEL = "dall-e-3"
    IMAGE_SIZE = "1024x1024"
    IMAGE_QUALITY = "standard"
    

    AVAILABLE_THEMES = [
        {"id": "espacio", "nombre": "Espacio", "descripcion": "Aventuras galácticas y exploración espacial"},
        {"id": "fantasia", "nombre": "Fantasía", "descripcion": "Mundos mágicos con dragones y hechiceros"},
        {"id": "vaqueros", "nombre": "Vaqueros", "descripcion": "El viejo oeste con cowboys y aventuras"},
        {"id": "piratas", "nombre": "Piratas", "descripcion": "Aventuras en el mar y búsqueda de tesoros"},
        {"id": "superheroes", "nombre": "Superhéroes", "descripcion": "Poderes especiales y salvando el mundo"},
        {"id": "dinosaurios", "nombre": "Dinosaurios", "descripcion": "Viajes al pasado prehistórico"},
        {"id": "robots", "nombre": "Robots", "descripcion": "Tecnología y robots del futuro"},
        {"id": "naturaleza", "nombre": "Naturaleza", "descripcion": "Animales y aventuras en la naturaleza"}
    ]
    
   
    THEME_DETAILS = {
        "espacio": {
            "elementos": ["astronautas", "planetas", "naves espaciales", "aliens amigables", "estrellas", "galaxias"],
            "valores": ["valentía", "curiosidad científica", "trabajo en equipo", "exploración", "ingenio"],
            "escenario": "el vasto universo lleno de maravillas",
            "estilo": "aventura espacial educativa"
        },
        "fantasia": {
            "elementos": ["hadas sabias", "dragones amigables", "castillos mágicos", "bosques encantados", "varitas", "pociones"],
            "valores": ["bondad", "coraje", "amistad", "magia del corazón", "sabiduría"],
            "escenario": "un reino mágico lleno de sorpresas",
            "estilo": "cuento de hadas moderno"
        },
        "vaqueros": {
            "elementos": ["cowboys valientes", "caballos fieles", "pueblos del oeste", "sheriffs justos", "duelos amistosos"],
            "valores": ["justicia", "valentía", "lealtad", "honestidad", "amistad"],
            "escenario": "el viejo oeste lleno de aventuras",
            "estilo": "western educativo"
        },
        "piratas": {
            "elementos": ["piratas aventureros", "tesoros misteriosos", "islas tropicales", "mapas secretos", "barcos"],
            "valores": ["valentía", "ingenio", "lealtad", "trabajo en equipo", "perseverancia"],
            "escenario": "los siete mares llenos de aventuras",
            "estilo": "aventura pirata educativa"
        },
        "naturaleza": {
            "elementos": ["animales del bosque", "ríos cristalinos", "árboles antiguos", "montañas", "flores mágicas"],
            "valores": ["respeto por la naturaleza", "cooperación", "cuidado ambiental", "compasión", "paciencia"],
            "escenario": "la hermosa naturaleza",
            "estilo": "cuento ecológico"
        }
    }
    

    LEVELS = {
        1: {"nombre": "Principiante", "puntos_min": 0, "color": "#4CAF50"},
        2: {"nombre": "Explorador", "puntos_min": 100, "color": "#2196F3"},
        3: {"nombre": "Aventurero", "puntos_min": 300, "color": "#FF9800"},
        4: {"nombre": "Héroe", "puntos_min": 600, "color": "#9C27B0"},
        5: {"nombre": "Leyenda", "puntos_min": 1000, "color": "#F44336"},
        6: {"nombre": "Maestro", "puntos_min": 1500, "color": "#FFD700"},
        7: {"nombre": "Sabio", "puntos_min": 2500, "color": "#E91E63"},
        8: {"nombre": "Campeón", "puntos_min": 4000, "color": "#9E9E9E"},
        9: {"nombre": "Legendario", "puntos_min": 6000, "color": "#FF5722"},
        10: {"nombre": "Inmortal", "puntos_min": 10000, "color": "#00BCD4"}
    }


# ============================================================================
# SERVICIO DE GENERACIÓN DE HISTORIAS
# ============================================================================

class StoryGenerationService:
    """
    HU-A3: Generar cuentos automáticamente según intereses del estudiante.

    """
    
    def __init__(self):
        """Inicializar servicio y verificar conexión con OpenAI"""
        
        # Validar que la API key existe
        if not AIConfig.OPENAI_API_KEY or len(AIConfig.OPENAI_API_KEY.strip()) < 20:
            raise Exception(
                "❌ OPENAI_API_KEY no configurada o inválida.\n"
                "Esta aplicación ES de IA - No funcionará sin ella."
            )
        
        try:
            self.client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)
            self.model = AIConfig.OPENAI_MODEL
            
            # PROBAR CONEXIÓN REAL
            print("🧪 Probando conexión con OpenAI...")
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            print("✅ OpenAI conectado y funcionando correctamente")
            
        except Exception as e:
            raise Exception(
                f"❌ Error conectando con OpenAI: {e}\n"
                "Esta aplicación requiere IA real para funcionar.\n"
                "Verifica tu API key y conexión a internet."
            )
    
    def generate_story(
        self, 
        theme: str, 
        character_name: str,
        age: int = 8,
        interests: List[str] = None
    ) -> Dict:
        """
        Genera una historia personalizada usando OpenAI.
        CRÍTICO: Si falla, lanza excepción. NO hay fallback.
        
        Args:
            theme: Tema principal (espacio, fantasía, etc.)
            character_name: Nombre del protagonista
            age: Edad del niño (para adaptar vocabulario)
            interests: Lista de intereses adicionales del alumno
        
        Returns:
            Dict con título, contenido, personajes y metadata
            
        Raises:
            Exception: Si no se puede generar la historia
        """
        
        try:
            # Construir prompt personalizado
            prompt = self._build_story_prompt(theme, character_name, age, interests)
            
            print(f"✨ Generando historia con IA: {character_name} - {theme}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un escritor profesional de literatura infantil. Creas historias apropiadas para niños que enseñan valores positivos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            if not content or len(content.split()) < 250:
                raise Exception(f"Historia generada demasiado corta: {len(content.split())} palabras")
            
           
            title = self._extract_title(content) or f"La Aventura de {character_name}"
            
        
            characters = self._extract_characters(content, character_name)
            
            print(f"✅ Historia generada: {len(content.split())} palabras")
            
            return {
                "title": title,
                "content": content,
                "theme": theme,
                "main_character": character_name,
                "characters": characters,
                "metadata": {
                    "word_count": len(content.split()),
                    "character_age": age,
                    "interests_used": interests or [],
                    "generated_with_real_ai": True
                }
            }
            
        except Exception as e:
            error_msg = f"❌ ERROR CRÍTICO generando historia con IA: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def _build_story_prompt(self, theme: str, character_name: str, age: int, interests: List[str]) -> str:
        """Construye el prompt para generar la historia"""
        
        theme_config = AIConfig.THEME_DETAILS.get(theme, AIConfig.THEME_DETAILS["fantasia"])
        interests_text = ""
        
        if interests:
            interests_text = f"El niño también disfruta de: {', '.join(interests)}. Incorpora estos elementos naturalmente. "
        
        prompt = f"""Escribe un cuento infantil COMPLETO de MÍNIMO 300 palabras para un niño de {age} años.

CONFIGURACIÓN ESPECÍFICA:
- Protagonista: {character_name} (edad: {age} años)
- Tema: {theme_config["estilo"]}
- Escenario: {theme_config["escenario"]}
- Elementos OBLIGATORIOS: {', '.join(theme_config["elementos"][:4])}
- Valores educativos: {', '.join(theme_config["valores"][:3])}
{interests_text}

ESTRUCTURA REQUERIDA:
1. INTRODUCCIÓN (70-80 palabras): Presentar a {character_name}, su personalidad y mundo
2. PROBLEMA/DESAFÍO (70-80 palabras): Conflicto específico que debe resolver
3. DESARROLLO (100 palabras): Cómo {character_name} enfrenta el desafío
4. CLÍMAX (40-50 palabras): Momento crucial de la resolución
5. RESOLUCIÓN (40-50 palabras): Solución exitosa y lección educativa

REQUISITOS ESTRICTOS:
- MÍNIMO 300 palabras
- Incluir diálogos realistas
- Detalles específicos y únicos de esta historia
- Lenguaje apropiado para {age} años
- Historia ÚNICA con eventos específicos
- Sin violencia, final positivo y educativo

Escribe SOLO la historia, sin títulos ni explicaciones adicionales."""
        
        return prompt
    
    def _extract_title(self, content: str) -> Optional[str]:
        """Extrae el título si está presente en el contenido"""
        lines = content.split('\n')
        for line in lines[:3]:
            if line.strip().startswith("Título:"):
                return line.replace("Título:", "").strip()
        return None
    
    def _extract_characters(self, content: str, main_character: str) -> List[str]:
        """Identifica personajes mencionados en la historia"""
        characters = [main_character]
        return characters


# ============================================================================
# SERVICIO DE GENERACIÓN DE PREGUNTAS
# ============================================================================

class QuestionGenerationService:
    """
    HU-A6: Generar 6 preguntas por historia (2 inferenciales, 2 críticas, 2 creativas).
    """
    
    def __init__(self):
        """Inicializar servicio"""
        
        # Validar API key
        if not AIConfig.OPENAI_API_KEY or len(AIConfig.OPENAI_API_KEY.strip()) < 20:
            raise Exception("❌ OPENAI_API_KEY no configurada. Esta aplicación requiere IA real.")
        
        try:
            self.client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)
            self.model = AIConfig.OPENAI_MODEL
            print("✅ QuestionGenerationService inicializado")
        except Exception as e:
            raise Exception(f"❌ Error inicializando QuestionGenerationService: {e}")
    
    def generate_questions(self, story_content: str, character_name: str) -> List[Dict]:
        """
        Genera 6 preguntas específicas sobre la historia.
        
        Returns:
            Lista de 6 preguntas con opciones múltiples
            
        Raises:
            Exception: Si no se pueden generar las preguntas
        """
        
        try:
            prompt = self._build_questions_prompt(story_content, character_name)
            
            print(f"❓ Generando 6 preguntas específicas con IA...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un pedagogo experto. Generas preguntas MUY específicas basadas en historias únicas. Las preguntas deben mencionar detalles específicos que solo aparecen en esa historia. Solo respondes con JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            questions_data = json.loads(content)
            
            # Validar estructura
            if not self._validate_questions_structure(questions_data):
                raise Exception("Estructura de preguntas inválida generada por IA")
            
            # Estructurar preguntas
            questions = self._structure_questions(questions_data)
            
            if len(questions) < 6:
                raise Exception(f"Solo se generaron {len(questions)} preguntas, se requieren 6")
            
            print(f"✅ {len(questions)} preguntas específicas generadas correctamente")
            return questions
            
        except Exception as e:
            error_msg = f"❌ ERROR CRÍTICO generando preguntas con IA: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def _build_questions_prompt(self, story_content: str, character_name: str) -> str:
        """Construye el prompt para generar preguntas"""
        
        return f"""Basándote en esta historia, genera EXACTAMENTE 6 preguntas de opción múltiple MUY ESPECÍFICAS:

HISTORIA:
{story_content}

GENERA:
- 2 preguntas INFERENCIALES (requieren deducir información implícita específica)
- 2 preguntas de JUICIO CRÍTICO (evalúan decisiones ESPECÍFICAS del protagonista)
- 2 preguntas CREATIVAS (imaginan alternativas basadas en EVENTOS ESPECÍFICOS)

FORMATO JSON:
{{
  "inferenciales": [
    {{
      "pregunta": "¿Por qué [EVENTO ESPECÍFICO de la historia]?",
      "opciones": ["opción incorrecta", "opción basada en la historia", "opción incorrecta", "opción incorrecta"],
      "respuesta_correcta": 1,
      "explicacion": "Basado en [DETALLE ESPECÍFICO de la historia]"
    }},
    {{
      "pregunta": "¿Qué podemos deducir sobre [DETALLE ESPECÍFICO]?",
      "opciones": ["opción incorrecta", "opción incorrecta", "opción correcta específica", "opción incorrecta"],
      "respuesta_correcta": 2,
      "explicacion": "Porque en la historia se menciona que..."
    }}
  ],
  "criticas": [
    {{
      "pregunta": "¿Fue correcta la decisión de {character_name} cuando [EVENTO EXACTO]?",
      "opciones": ["opción incorrecta", "opción incorrecta", "opción incorrecta", "Sí, porque [razón específica]"],
      "respuesta_correcta": 3,
      "explicacion": "Esta decisión fue acertada porque..."
    }},
    {{
      "pregunta": "¿Qué valor demostró {character_name} en [SITUACIÓN ESPECÍFICA]?",
      "opciones": ["Valor correcto según la historia", "valor opuesto", "valor irrelevante", "ningún valor"],
      "respuesta_correcta": 0,
      "explicacion": "Se ve este valor cuando..."
    }}
  ],
  "creativas": [
    {{
      "pregunta": "¿Qué habría pasado si {character_name} hubiera [ALTERNATIVA] en lugar de [ACCIÓN REAL]?",
      "opciones": ["resultado ilógico", "Resultado lógico basado en la historia", "resultado imposible", "resultado genérico"],
      "respuesta_correcta": 1,
      "explicacion": "Basándose en los elementos de la historia..."
    }},
    {{
      "pregunta": "¿Cómo podría continuar la historia con [ELEMENTO ÚNICO ESPECÍFICO]?",
      "opciones": ["continuación genérica", "continuación ilógica", "continuación que contradice", "Continuación coherente con elementos únicos"],
      "respuesta_correcta": 3,
      "explicacion": "Esta continuación tiene sentido porque..."
    }}
  ]
}}

REQUISITOS CRÍTICOS:
- TODAS las preguntas deben mencionar eventos, nombres o detalles ESPECÍFICOS de esta historia
- Las opciones correctas deben basarse en información que SOLO está en esta historia
- Evitar preguntas genéricas que puedan aplicar a cualquier historia
- Mencionar al protagonista {character_name} en las preguntas cuando sea relevante
- 4 opciones por pregunta
- Una sola respuesta correcta (índice 0-3)
- IMPORTANTE: La respuesta correcta debe estar en DIFERENTES POSICIONES (0, 1, 2 o 3) para cada pregunta
- NO poner todas las respuestas correctas en la posición 0
- Randomizar la ubicación de la respuesta correcta entre las 4 opciones

Responde SOLO con JSON válido."""
        
    def _validate_questions_structure(self, questions_data: Dict) -> bool:
        """Valida que las preguntas tengan la estructura correcta"""
        
        required_sections = ["inferenciales", "criticas", "creativas"]
        
        for section in required_sections:
            if section not in questions_data:
                print(f"❌ Sección faltante: {section}")
                return False
            
            if len(questions_data[section]) != 2:
                print(f"❌ Sección {section} debe tener exactamente 2 preguntas")
                return False
            
            for pregunta in questions_data[section]:
                if not all(key in pregunta for key in ["pregunta", "opciones", "respuesta_correcta"]):
                    print(f"❌ Estructura incorrecta en {section}")
                    return False
                
                if len(pregunta["opciones"]) != 4:
                    print(f"❌ Debe haber exactamente 4 opciones")
                    return False
        
        return True
    
    def _structure_questions(self, questions_data: Dict) -> List[Dict]:
        """Estructura las preguntas en formato estándar"""
        
        questions = []
        order = 0
        
        type_mapping = {
            "inferenciales": "inferencial",
            "criticas": "critica",
            "creativas": "creativa"
        }
        
        for question_type, db_type in type_mapping.items():
            if question_type in questions_data:
                for q in questions_data[question_type]:
                    questions.append({
                        "question_text": q["pregunta"],
                        "question_type": db_type,
                        "options": q["opciones"],
                        "correct_option": q["respuesta_correcta"],
                        "explanation": q.get("explicacion", ""),
                        "order_index": order,
                        "points_value": 20
                    })
                    order += 1
        
        return questions


# ============================================================================
# SERVICIO DE GENERACIÓN DE IMÁGENES
# ============================================================================

class ImageGenerationService:
    """
    HU-A5: Generar imágenes de personajes usando DALL-E.
    """
    
    def __init__(self):
        """Inicializar servicio"""
        
        # Validar API key
        if not AIConfig.OPENAI_API_KEY or len(AIConfig.OPENAI_API_KEY.strip()) < 20:
            raise Exception("❌ OPENAI_API_KEY no configurada. Esta aplicación requiere IA real.")
        
        try:
            self.client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)
            print("✅ ImageGenerationService inicializado")
        except Exception as e:
            raise Exception(f"❌ Error inicializando ImageGenerationService: {e}")
    
    def generate_character_image(
        self, 
        character_name: str, 
        theme: str,
        age: int = 8,
        story_context: str = ""
    ) -> str:
        """
        Genera imagen del personaje usando DALL-E.
        
        Returns:
            URL de la imagen generada
            
        Raises:
            Exception: Si no se puede generar la imagen
        """
        
        try:
            prompt = self._build_image_prompt(character_name, theme, age, story_context)
            
            print(f"🎨 Generando imagen con DALL-E para {character_name}...")
            
            response = self.client.images.generate(
                model=AIConfig.IMAGE_MODEL,
                prompt=prompt,
                size=AIConfig.IMAGE_SIZE,
                quality=AIConfig.IMAGE_QUALITY,
                n=1
            )
            
            image_url = response.data[0].url
            
            print(f"✅ Imagen generada correctamente")
            return image_url
            
        except Exception as e:
            error_msg = f"❌ ERROR CRÍTICO generando imagen con DALL-E: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def _build_image_prompt(self, character_name: str, theme: str, age: int, story_context: str) -> str:
        """Construye prompt para generación de imagen"""
        
        style = "children's book illustration style, colorful, friendly, cartoon"
        
        prompt = f"""A friendly {age}-year-old character named {character_name} in a {theme} setting.
{story_context[:200] if story_context else ''}
Style: {style}.
Safe for children, positive, encouraging expression."""
        
        return prompt




class GamificationService:
    """
    HU-A8, HU-A9: Sistema de puntos, niveles y mensajes motivacionales.
    """
    
    @staticmethod
    def calculate_points(
        correct_answers: int,
        total_questions: int,
        time_average: float = None,
        is_perfect: bool = False
    ) -> Dict:
        """Calcula puntos con bonificaciones"""
        
        points_per_question = 20
        base_points = correct_answers * points_per_question
        
        bonuses = []
        bonus_points = 0
        
        
        bonus_points += 50
        bonuses.append({"name": "Historia completada", "points": 50})
        
        
        if is_perfect or (correct_answers == total_questions == 6):
            bonus_points += 100
            bonuses.append({"name": "¡Respuestas perfectas!", "points": 100})
        
    
        if time_average and time_average < 30:
            speed_bonus = correct_answers * 5
            bonus_points += speed_bonus
            bonuses.append({"name": "Velocidad mental", "points": speed_bonus})
        
        
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        if percentage >= 80:
            bonus_points += 30
            bonuses.append({"name": "Excelente comprensión", "points": 30})
        
        total_points = base_points + bonus_points
        
        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": total_points,
            "bonuses": bonuses,
            "accuracy": percentage
        }
    
    @staticmethod
    def calculate_level(total_points: int) -> Dict:
        """Calcula nivel del alumno basado en puntos totales"""
        
        current_level = 1
        
        for level, info in AIConfig.LEVELS.items():
            if total_points >= info["puntos_min"]:
                current_level = level
            else:
                break
        
        level_info = AIConfig.LEVELS[current_level]
        next_level = current_level + 1 if current_level < 10 else 10
        
        if next_level <= 10 and next_level > current_level:
            next_level_points = AIConfig.LEVELS[next_level]["puntos_min"]
            points_range = next_level_points - level_info["puntos_min"]
            current_progress = total_points - level_info["puntos_min"]
            progress_percentage = min(100, (current_progress / points_range) * 100) if points_range > 0 else 100
        else:
            progress_percentage = 100
        
        return {
            "level": current_level,
            "level_name": level_info["nombre"],
            "color": level_info["color"],
            "current_points": total_points,
            "required_points": level_info["puntos_min"],
            "progress_percentage": round(progress_percentage, 1),
            "is_max_level": current_level == 10
        }
    
    @staticmethod
    def generate_congratulation_message(correct: int, total: int, points: int) -> str:
        """HU-A10: Genera mensaje de felicitación personalizado"""
        
        percentage = (correct / total) * 100 if total > 0 else 0
        
        if percentage == 100:
            messages = [
                f"¡INCREÍBLE! ¡Perfecto! ¡Eres un genio! 🧠⭐ (+{points} puntos)",
                f"¡FANTÁSTICO! ¡Comprensión perfecta! 💯🎉 (+{points} puntos)",
                f"¡WOW! ¡Todas correctas! ¡Eres brillante! 🌟✨ (+{points} puntos)"
            ]
        elif percentage >= 80:
            messages = [
                f"¡EXCELENTE! ¡Muy buena comprensión! 🌟 (+{points} puntos)",
                f"¡MUY BIEN! ¡Entendiste muy bien! 👏 (+{points} puntos)",
                f"¡GENIAL! ¡Sigue así! 🚀 (+{points} puntos)"
            ]
        elif percentage >= 60:
            messages = [
                f"¡BIEN HECHO! ¡Vas por buen camino! 💪 (+{points} puntos)",
                f"¡SIGUE ASÍ! ¡Cada vez mejor! 📈 (+{points} puntos)"
            ]
        else:
            messages = [
                f"¡BUEN INTENTO! ¡Sigue practicando! 🌱 (+{points} puntos)",
                f"¡NO TE RINDAS! ¡Aprendes con cada historia! 📚 (+{points} puntos)"
            ]
        
        import random
        return random.choice(messages)




class PromptPersonalizationService:
    """HU-A2: Generar prompts automáticamente según intereses del estudiante"""
    
    @staticmethod
    def generate_personalized_prompt(theme: str, interests: List[str], age: int) -> str:
        """Genera un prompt optimizado basado en el perfil del estudiante"""
        
        theme_config = AIConfig.THEME_DETAILS.get(theme, AIConfig.THEME_DETAILS["fantasia"])
        interests_text = ", ".join(interests) if interests else theme
        
        prompt = f"""Crea una historia emocionante para un niño de {age} años que le encanta {interests_text}.

La historia debe:
- Estar ambientada en el mundo de {theme_config["estilo"]}
- Incluir elementos como: {', '.join(theme_config["elementos"][:3])}
- Transmitir valores de: {', '.join(theme_config["valores"][:2])}
- Tener un protagonista valiente y amigable
- Ser apropiada para la edad
- Tener aproximadamente 300 palabras

Hazla memorable y educativa."""
        
        return prompt
    
    @staticmethod
    def get_available_themes() -> List[Dict]:
        """Retorna los temas disponibles"""
        return AIConfig.AVAILABLE_THEMES




__all__ = [
    'StoryGenerationService',
    'QuestionGenerationService', 
    'ImageGenerationService',
    'GamificationService',
    'PromptPersonalizationService',
    'AIConfig'
]


