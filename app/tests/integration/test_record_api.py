import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def create_student_and_story():
    # Registramos usuario tipo student
    user_resp = client.post("/api/v1/auth/register", json={
        "fullname": "Student Record",
        "email": "student_record@example.com",
        "password": "password123",
        "tipo": "student"
    })
    assert user_resp.status_code == 200
    user = user_resp.json()

    # Crear perfil Student
    student_resp = client.post("/api/v1/students/", json={
        "user_id": user["id"],
        "birth_date": None,
        "current_grade": "5to",
        "interests": "ciencia, cuentos"
    })
    assert student_resp.status_code == 200
    student = student_resp.json()

    # Crear historia
    story_resp = client.post("/api/v1/stories/", json={
        "title": "Historia de prueba",
        "content": "Un cuento educativo",
        "student_id": student["id"],
        "topic": "educacion",
        "question_answer": [],
        "story_metadata": {},
        "characters": []
    })
    assert story_resp.status_code == 200
    story = story_resp.json()
    print("📥 Story response:", story)

    return user, student, story


def test_create_record_success(create_student_and_story):
    user, student, story = create_student_and_story
    response = client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    })
    assert response.status_code == 200
    record = response.json()
    assert record["student_id"] == student["id"]
    assert record["story_id"] == story["id"]


def test_update_record_success(create_student_and_story):
    user, student, story = create_student_and_story
    record_resp = client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    })
    record = record_resp.json()

    response = client.patch(f"/api/v1/records/{record['id']}", json={"status": "COMPLETED"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "COMPLETED"


def test_get_student_records(create_student_and_story):
    user, student, story = create_student_and_story
    client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    })

    response = client.get(f"/api/v1/records/student/{student['id']}")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert records[0]["student_id"] == student["id"]


def test_save_answer_and_get_detail(create_student_and_story):
    user, student, story = create_student_and_story
    record = client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    }).json()

    answer_resp = client.post(f"/api/v1/records/{record['id']}/answers", json={
        "question_index": 0,
        "response": "A",
        "is_correct": True
    })
    assert answer_resp.status_code == 200
    answer = answer_resp.json()
    assert answer["question_index"] == 0
    assert answer["is_correct"] is True

    detail = client.get(f"/api/v1/records/{record['id']}")
    assert detail.status_code == 200
    record_detail = detail.json()
    assert len(record_detail["answers"]) > 0


def test_save_progress_bulk(create_student_and_story):
    user, student, story = create_student_and_story
    record = client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    }).json()

    payload = [
        {"question_index": 0, "response": "A", "is_correct": True},
        {"question_index": 1, "response": "B", "is_correct": False},
    ]
    resp = client.post(f"/api/v1/records/{record['id']}/save-progress", json=payload)
    assert resp.status_code == 200
    assert resp.json()["answers_saved"] == 2


def test_restart_exam(create_student_and_story):
    user, student, story = create_student_and_story
    record = client.post(f"/api/v1/records/?user_id={user['id']}", json={
        "story_id": story["id"],
        "correct_answers": 0,
        "total_questions": 6,
        "points": 0
    }).json()

    resp = client.post(f"/api/v1/records/{record['id']}/restart")
    assert resp.status_code == 200
    restarted = resp.json()
    assert restarted["status"] == "IN_PROGRESS"
    assert restarted["correct_answers"] == 0
