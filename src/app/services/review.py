from app.models.review import Review, ReviewCreate
from app.repositories.review_repository import ReviewRepository


class ReviewService:
    def __init__(self, repository: ReviewRepository) -> None:
        self.repository = repository

    def create(self, analysis_id: str, review: ReviewCreate) -> Review:
        return self.repository.save(Review(analysis_id=analysis_id, **review.model_dump()))
