from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    students,
    teachers,
    stories,
    records,
    enrollments,
    questions,
    gamification
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
api_router.include_router(stories.router, prefix="/stories", tags=["Stories"])
api_router.include_router(records.router, prefix="/records", tags=["Records"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])