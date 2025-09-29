from sqlalchemy.orm import Session
from app.db.repositories import StoryRepository

story_repo = StoryRepository()

class StoryService:
    @staticmethod
    def create_story(db: Session, data: dict):
        return story_repo.create(db, data)

    @staticmethod
    def list_stories(db: Session, skip: int = 0, limit: int = 50):
        return story_repo.list(db, skip=skip, limit=limit)
