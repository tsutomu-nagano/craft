from app.models.review import Review
from app.repositories.database import ReviewRecord, SessionLocal


class ReviewRepository:
    def save(self, review: Review) -> Review:
        with SessionLocal() as session:
            record = ReviewRecord(**review.model_dump(mode="json"))
            session.merge(record)
            session.commit()
        return review

    def list(self) -> list[ReviewRecord]:
        with SessionLocal() as session:
            return list(session.query(ReviewRecord).order_by(ReviewRecord.reviewed_at.desc()).all())
