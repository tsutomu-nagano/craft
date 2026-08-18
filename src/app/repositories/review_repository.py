from __future__ import annotations

from app.models.review import Review, ReviewUpdate
from app.repositories.database import ReviewRecord, SessionLocal


class ReviewRepository:
    def save(self, review: Review) -> Review:
        with SessionLocal() as session:
            record = ReviewRecord(**review.model_dump())
            session.merge(record)
            session.commit()
        return review

    def list(self) -> list[ReviewRecord]:
        with SessionLocal() as session:
            return list(session.query(ReviewRecord).order_by(ReviewRecord.reviewed_at.desc()).all())

    def list_by_analysis(self, analysis_id: str) -> list[ReviewRecord]:
        with SessionLocal() as session:
            return list(
                session.query(ReviewRecord)
                .filter(ReviewRecord.analysis_id == analysis_id)
                .order_by(ReviewRecord.reviewed_at.desc())
                .all()
            )

    def get(self, review_id: str) -> ReviewRecord | None:
        with SessionLocal() as session:
            return session.get(ReviewRecord, review_id)

    def delete_by_analysis(self, analysis_id: str) -> int:
        with SessionLocal() as session:
            count = (
                session.query(ReviewRecord)
                .filter(ReviewRecord.analysis_id == analysis_id)
                .delete(synchronize_session=False)
            )
            session.commit()
            return count

    def update(self, review_id: str, update: ReviewUpdate) -> ReviewRecord | None:
        with SessionLocal() as session:
            record = session.get(ReviewRecord, review_id)
            if record is None:
                return None
            for key, value in update.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(record, key, value)
            session.commit()
            session.refresh(record)
            return record
