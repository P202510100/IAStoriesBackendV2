from sqlalchemy.orm import Session
from app.db.repositories import StoryRepository, StudentRepository
import json

from app.schemas import StoryGenerateRequest, RecordCreate, StoryRead, story
from app.services.ai_service import generar_historia_preguntas_imagen
from app.services.record_service import RecordService

story_repo = StoryRepository()
student_repo = StudentRepository()

class StoryService:
    @staticmethod
    def create_story(db: Session, data: dict):
        return story_repo.create(db, data)

    @staticmethod
    def generate_story(db: Session, data: StoryGenerateRequest):
        # 1. Obtener al alumno (para sacar su grado escolar)
        student = student_repo.get_by_user_id(db, data.user_id)
        if not student:
            raise ValueError("Alumno no encontrado")

        grado = student.current_grade or "sin grado"

        # 2. Generar historia con IA usando los datos que vienen del frontend
        ai_result = generar_historia_preguntas_imagen(
            nombre=data.nombre,
            edad=data.edad,
            elementos=data.elementos,
            grado=grado,
            topic=data.topic
        )

        # Normalización de preguntas
        normalized_questions = []
        tipos_validos = ["inferencial", "juicio_critico", "creativa"]

        for i, q in enumerate(ai_result.get("questions", [])):
            question = {
                "question": q.get("question", f"Pregunta {i + 1}"),
                "options": q.get("options", [])[:4],
                "answer": q.get("answer", 0),
                "type": q.get("type", tipos_validos[i % 3])
            }
            normalized_questions.append(question)

        # 3. Preparar objeto para BD
        story_data = {
            "title": ai_result["title"],
            "content": ai_result["content"],
            "topic": data.topic,
            "question_answer": normalized_questions,
            "story_metadata": ai_result.get("story_metadata", {}),
            "characters": ai_result.get("characters", []),
            "student_id": student.id,
            "image_b64": ai_result.get("image_b64")
        }

        story = story_repo.create(db, story_data)

        # 4. Crear record asociado en estado IN_PROGRESS
        record_payload = RecordCreate(
            story_id=story.id,
            correct_answers=0,
            total_questions=len(normalized_questions),
            points=0
        )

        record = RecordService.create_record_for_student(db, data.user_id ,record_payload)

        story_read = StoryRead.model_validate(story)
        story_read.record_id = record.id

        # 5. Retornar historia + record_id
        return story_read



    @staticmethod
    def list_stories(db: Session, skip: int = 0, limit: int = 50):
        return story_repo.list(db, skip=skip, limit=limit)


    @staticmethod
    def list_stories_by_student(db: Session, student_id: int, skip: int = 0, limit: int = 50):
        return story_repo.list_by_student(db, student_id, skip=skip, limit=limit)
