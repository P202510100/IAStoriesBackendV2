from sqlalchemy.orm import Session
from app.db.repositories import RecordRepository, StudentRepository, StoryRepository, AnswerRepository
from app.schemas.answer import AnswerCreate
from app.schemas.record import RecordCreate, RecordUpdate
from app.models.models import Record as RecordModel, Student
from app.models.models import Answer, User, Record
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from typing import Optional, List
from sqlalchemy import func

record_repo = RecordRepository()
student_repo = StudentRepository()
story_repo = StoryRepository()
answer_repo = AnswerRepository()

class RecordService:
    @staticmethod
    def create_record_for_student(db: Session, user_id: int, payload: RecordCreate) -> RecordModel:
        student = student_repo.get_by_user_id(db, user_id)
        if not student:
            raise ValueError("Perfil de estudiante no encontrado")

        story = story_repo.get(db, payload.story_id)
        if not story:
            raise ValueError("Historia no encontrada")

        points = payload.points if payload.points is not None else payload.correct_answers

        record = record_repo.create(db, {
            "story_id": payload.story_id,
            "student_id": student.id,
            "points": points,
            "correct_answers": payload.correct_answers,
            "total_questions": payload.total_questions,
            "status": "IN_PROGRESS",
            "completed_at": None
        })

        return record

    @staticmethod
    def update_record(db: Session, record_id: int, payload: RecordUpdate) -> RecordModel:
        record = record_repo.get(db, record_id)
        if not record:
            raise ValueError("Record no encontrado")

        update_data = payload.model_dump(exclude_unset=True)

        # Si marcan como COMPLETED
        if update_data.get("status") == "COMPLETED":
            update_data["completed_at"] = datetime.now(timezone.utc)

            # Calcular puntos y correctas a partir de las respuestas
            answers = answer_repo.list_by_record(db, record_id)  # <-- necesitas este método en el repo
            correct_answers = sum(1 for a in answers if a.is_correct)
            total_questions = len(record.story.question_answer or [])
            points = correct_answers  # lógica de puntos, aquí igual a correctas

            update_data["correct_answers"] = correct_answers
            update_data["total_questions"] = total_questions
            update_data["points"] = points

            # actualizamos puntos acumulados del estudiante
            student = student_repo.get(db, record.student_id)
            if student:
                student_repo.update(db, student, {
                    "total_points": student.total_points + points,
                    "last_updated_date": datetime.now(timezone.utc)
                })

        record = record_repo.update(db, record, update_data)
        return record

    @staticmethod
    def save_answer(db: Session, record_id: int, question_index: int, response: str,
                    is_correct: bool | None = None) -> Answer:
        record = record_repo.get(db, record_id)
        if not record:
            raise ValueError("Record no encontrado")

        # ¿Ya había respuesta para esa pregunta?
        answer = answer_repo.get_by_record_and_question(db, record_id, question_index)

        if answer:
            # Actualizar
            answer = answer_repo.update(db, answer, {
                "response": response,
                "is_correct": is_correct
            })
        else:
            # Crear nueva
            answer = answer_repo.create(db, {
                "record_id": record_id,
                "question_index": question_index,
                "response": response,
                "is_correct": is_correct
            })

        return answer

    @staticmethod
    def get_record_with_answers(db: Session, record_id: int) -> RecordModel:
        record = (
            db.query(RecordModel)
            .options(joinedload(RecordModel.story), joinedload(RecordModel.answers))
            .filter(RecordModel.id == record_id)
            .first()
        )
        return record

    @staticmethod
    def save_progress_bulk(db: Session, record_id: int, answers: List[AnswerCreate]):
        record = record_repo.get(db, record_id)
        if not record:
            raise ValueError("Record no encontrado")

        saved = []
        for ans in answers:
            saved_answer = RecordService.save_answer(
                db=db,
                record_id=record_id,
                question_index=ans.question_index,
                response=ans.response,
                is_correct=ans.is_correct
            )
            saved.append(saved_answer)

        # Hacemos commit al final para evitar race conditions
        db.commit()
        return saved

    @staticmethod
    def restart_exam(db: Session, record_id: int):
        record = db.query(RecordModel).filter(RecordModel.id == record_id).first()
        if not record:
            raise ValueError("Record not found")

        if record.has_restarted:
            raise ValueError("Este examen ya fue reiniciado una vez. No se puede volver a reiniciar.")

        # Borrar todas las respuestas
        db.query(Answer).filter(Answer.record_id == record_id).delete()

        # Reiniciar estado
        record.status = "IN_PROGRESS"
        record.correct_answers = 0
        record.points = 0
        record.completed_at = None
        record.has_restarted = True  # marcar que ya usó el reinicio

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_class_ranking(db: Session):
        """
                Calcula el ranking general de la clase directamente desde la tabla Record,
                incluyendo precisión promedio, total de historias y puntos globales.
                """

        # Subconsulta: sumar métricas por estudiante
        results = (
            db.query(
                Student.id.label("student_id"),
                User.fullname.label("nombre"),
                func.sum(func.coalesce(Record.points, 0)).label("puntos"),
                func.count(Record.id).filter(Record.status == "COMPLETED").label("historias"),
                func.sum(func.coalesce(Record.correct_answers, 0)).label("correctas"),
                func.sum(func.coalesce(Record.total_questions, 0)).label("preguntas")
            )
            .join(User, Student.user_id == User.id)
            .join(Record, Record.student_id == Student.id)
            .group_by(Student.id, User.fullname)
            .all()
        )

        ranking = []
        total_correct = 0
        total_questions = 0
        total_points = 0
        total_histories = 0

        for row in results:
            correctas = row.correctas or 0
            preguntas = row.preguntas or 0
            precision = round((correctas / preguntas) * 100, 2) if preguntas > 0 else 0

            ranking.append({
                "id": row.student_id,
                "nombre": row.nombre,
                "puntos": row.puntos or 0,
                "historias": row.historias or 0,
                "precision": precision,
                "respuestas_correctas": correctas,
                "total_respuestas": preguntas
            })

            total_correct += correctas
            total_questions += preguntas
            total_points += row.puntos or 0
            total_histories += row.historias or 0

        promedio_clase = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0

        estadisticas = {
            "promedioClase": promedio_clase,
            "historiasTotal": total_histories,
            "puntosTotal": total_points
        }

        # Orden descendente por puntos
        ranking.sort(key=lambda x: x["puntos"], reverse=True)

        return {"ranking": ranking, "estadisticas": estadisticas}

