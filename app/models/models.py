from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class UserType(enum.Enum):
    student = "student"
    teacher = "teacher"

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

    user = relationship("User", back_populates="student_profile")
    records = relationship("Record", back_populates="student")

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    current_school = Column(String(255))
    alma_mater = Column(String(255))
    degree_level = Column(String(100))
    major = Column(String(255))

    user = relationship("User", back_populates="teacher_profile")

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
