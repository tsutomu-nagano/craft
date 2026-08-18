from fastapi import APIRouter

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
