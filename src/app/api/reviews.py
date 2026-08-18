from fastapi import APIRouter, HTTPException

from app.models.review import ReviewUpdate
from app.repositories.review_repository import ReviewRepository

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("")
def list_reviews() -> list[dict]:
    return [
        {
            "review_id": item.review_id,
            "analysis_id": item.analysis_id,
            "target_issue": item.target_issue,
            "human_decision": item.human_decision,
            "reviewer": item.reviewer,
            "reviewed_at": item.reviewed_at,
        }
        for item in ReviewRepository().list()
    ]


@router.patch("/{review_id}")
def update_review(review_id: str, request: ReviewUpdate) -> dict:
    item = ReviewRepository().update(review_id, request)
    if item is None:
        raise HTTPException(status_code=404, detail="review not found")
    return {
        "review_id": item.review_id,
        "analysis_id": item.analysis_id,
        "target_issue": item.target_issue,
        "ai_judgement": item.ai_judgement,
        "human_decision": item.human_decision,
        "corrected_content": item.corrected_content,
        "reason": item.reason,
        "comment": item.comment,
        "reviewer": item.reviewer,
        "reviewed_at": item.reviewed_at,
    }
