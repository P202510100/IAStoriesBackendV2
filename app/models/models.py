
"""
Modelos completos para IAStoriesBackendV2
Mantiene nombres existentes y agrega funcionalidades faltantes
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, Enum, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base




class UserType(enum.Enum):
    student = "student"
    teacher = "teacher"
    

class QuestionType(enum.Enum):
    """Tipos de preguntas según las HUs"""
    inferencial = "inferencial"
    critica = "critica"
    creativa = "creativa"


class DifficultyLevel(enum.Enum):
    """Niveles de dificultad"""
    facil = "facil"
    medio = "medio"
    dificil = "dificil"



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    tipo = Column(Enum(UserType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    
    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    birth_date = Column(Date)
    current_grade = Column(String(50))
    interests = Column(Text)  
    total_points = Column(Integer, default=0)  
    last_updated_date = Column(DateTime, default=datetime.utcnow)
    current_level = Column(Integer, default=1)  
    
    classroom_code = Column(String(10), nullable=True)  
    streak_days = Column(Integer, default=0)  
    achievements = Column(JSON, default=list)  
    level_name = Column(String(50), default="Principiante") 

    
    user = relationship("User", back_populates="student_profile")
    records = relationship("Record", back_populates="student")
    
   
    answers = relationship("Answer", back_populates="student", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="student", cascade="all, delete-orphan")
    achievements_unlocked = relationship("Achievement", back_populates="student", cascade="all, delete-orphan")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    current_school = Column(String(255))
    alma_mater = Column(String(255))
    degree_level = Column(String(100))
    major = Column(String(255))
    
    
    classroom_code = Column(String(10), unique=True, nullable=True)  
    classroom_name = Column(String(100), default="Mi Clase") 
    invitation_enabled = Column(Boolean, default=True)  

    
    user = relationship("User", back_populates="teacher_profile")
    
    
    invitations = relationship("Invitation", back_populates="teacher", cascade="all, delete-orphan")


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    topic = Column(String(100))
    question_answer = Column(Text)
    story_metadata = Column(Text)
    characters = Column(Text)
    alumno_id = Column(Integer, ForeignKey("students.id"))  
    created_at = Column(DateTime, default=datetime.utcnow)
    
   
    questions = relationship("Question", back_populates="story", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="story", cascade="all, delete-orphan")


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    points = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)

    
    student = relationship("Student", back_populates="records")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    student_id = Column(Integer, ForeignKey("students.id"))




class Question(Base):
    """
    HU-A6: Modelo de preguntas por historia.
    Cada historia genera 6 preguntas (2 inferenciales, 2 críticas, 2 creativas).
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
   
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.medio)
    
    
    options = Column(JSON)  
    correct_option = Column(Integer, nullable=True)
    
   
    explanation = Column(Text, nullable=True) 
    points_value = Column(Integer, default=20)  
    order_index = Column(Integer, default=0)  
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
  
    story = relationship("Story", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "story_id": self.story_id,
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "difficulty": self.difficulty.value,
            "options": self.options,
            "correct_option": self.correct_option,
            "explanation": self.explanation,
            "points_value": self.points_value,
            "order_index": self.order_index
        }


class Answer(Base):
    """
    HU-A7, HU-A8: Respuestas de alumnos a preguntas.
    Incluye sistema de repetición y puntos.
    """
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Respuesta del alumno
    selected_option = Column(Integer, nullable=True)  # Para preguntas de opción múltiple
    text_answer = Column(Text, nullable=True)  # Para preguntas abiertas
    
    # Evaluación
    is_correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0)
    attempt_number = Column(Integer, default=1)  # HU-A7: Permitir repetir
    
    # Metadata
    time_spent = Column(Float, nullable=True)  # Tiempo en segundos
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    question = relationship("Question", back_populates="answers")
    student = relationship("Student", back_populates="answers")
    
    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "student_id": self.student_id,
            "selected_option": self.selected_option,
            "is_correct": self.is_correct,
            "points_earned": self.points_earned,
            "attempt_number": self.attempt_number,
            "answered_at": self.answered_at.isoformat()
        }


class Progress(Base):
    """
    HU-A11, HU-D3: Tracking de progreso detallado de alumnos.
    Registra cada sesión y actividad del alumno.
    """
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)
    
   
    session_date = Column(DateTime, default=datetime.utcnow)
    stories_completed = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_points_session = Column(Integer, default=0)
    
   
    inferential_correct = Column(Integer, default=0)
    inferential_total = Column(Integer, default=0)
    critical_correct = Column(Integer, default=0)
    critical_total = Column(Integer, default=0)
    creative_correct = Column(Integer, default=0)
    creative_total = Column(Integer, default=0)
    
   
    session_duration = Column(Float, nullable=True)  
    
    
    student = relationship("Student", back_populates="progress_records")
    story = relationship("Story", back_populates="progress_records")
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "story_id": self.story_id,
            "session_date": self.session_date.isoformat(),
            "stories_completed": self.stories_completed,
            "questions_answered": self.questions_answered,
            "correct_answers": self.correct_answers,
            "total_points_session": self.total_points_session,
            "accuracy": (self.correct_answers / self.questions_answered * 100) if self.questions_answered > 0 else 0,
            "by_type": {
                "inferential": {
                    "correct": self.inferential_correct,
                    "total": self.inferential_total
                },
                "critical": {
                    "correct": self.critical_correct,
                    "total": self.critical_total
                },
                "creative": {
                    "correct": self.creative_correct,
                    "total": self.creative_total
                }
            }
        }


class Invitation(Base):
    """
    HU-D1: Sistema de invitaciones para asociar estudiantes.
    Soporta invitación por email y por código de clase.
    """
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    
    
    invitation_type = Column(String(20))  # "email" o "code"
    
    
    student_email = Column(String(255), nullable=True)
    custom_message = Column(Text, nullable=True)
    
    
    classroom_code = Column(String(10), nullable=True)
    
    
    status = Column(String(20), default="pending")
    expires_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    accepted_by = Column(Integer, ForeignKey("students.id"), nullable=True)
    
   
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    teacher = relationship("Teacher", back_populates="invitations")
    
    def to_dict(self):
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "invitation_type": self.invitation_type,
            "student_email": self.student_email,
            "classroom_code": self.classroom_code,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class Achievement(Base):
    """
    Sistema de logros para gamificación adicional.
    """
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    achievement_key = Column(String(50), nullable=False) 
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="🏆")
    
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    student = relationship("Student", back_populates="achievements_unlocked")
    
    def to_dict(self):
        return {
            "id": self.id,
            "achievement_key": self.achievement_key,
            "achievement_name": self.achievement_name,
            "description": self.description,
            "icon": self.icon,
            "unlocked_at": self.unlocked_at.isoformat()
        }
