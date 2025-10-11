import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def create_teacher_and_student():
    # Crear usuario teacher
    teacher_user = client.post("/api/v1/auth/register", json={
        "fullname": "Profesor Test",
        "email": "teacher_test@example.com",
        "password": "password123",
        "tipo": "teacher"
    }).json()

    # Crear perfil Teacher
    teacher_profile = client.post("/api/v1/teachers/", json={
        "user_id": teacher_user["id"],
        "current_school": "Colegio Nacional",
        "alma_mater": "Universidad Nacional",
        "degree_level": "Licenciatura",
        "major": "Educación"
    }).json()

    # Crear usuario student
    student_user = client.post("/api/v1/auth/register", json={
        "fullname": "Alumno Test",
        "email": "student_test@example.com",
        "password": "password123",
        "tipo": "student"
    }).json()

    # Crear perfil Student
    student_profile = client.post("/api/v1/students/", json={
        "user_id": student_user["id"],
        "birth_date": None,
        "current_grade": "5to",
        "interests": "matemáticas, lectura"
    }).json()

    return teacher_profile, student_profile

def test_enroll_and_unenroll_student(create_teacher_and_student):
    teacher, student = create_teacher_and_student

    # 1. Enroll student
    enroll_resp = client.post("/api/v1/enrollments/", json={
        "teacher_id": teacher["id"],   # ✅ ahora es el ID del teacher_profile
        "student_id": student["id"]
    })
    assert enroll_resp.status_code == 200
    enrollment = enroll_resp.json()
    assert enrollment["teacher_id"] == teacher["id"]
    assert enrollment["student_id"] == student["id"]

    # 2. Get students for teacher
    list_resp = client.get(f"/api/v1/enrollments/teacher/{teacher['id']}/students")
    assert list_resp.status_code == 200
    students_list = list_resp.json()
    assert any(s["id"] == student["id"] for s in students_list)

    # 3. Unenroll student
    unenroll_resp = client.delete(f"/api/v1/enrollments/{teacher['id']}/{student['id']}")
    assert unenroll_resp.status_code == 200
