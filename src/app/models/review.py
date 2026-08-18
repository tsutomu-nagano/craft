from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class ReviewDecision(StrEnum):
    APPROVED = "approved"
    CORRECTED = "corrected"
    REJECTED = "rejected"
    NEEDS_INVESTIGATION = "needs_investigation"


class ReviewCreate(BaseModel):
    target_issue: str
    ai_judgement: str | None = None
    human_decision: ReviewDecision
    corrected_content: str | None = None
    reason: str | None = None
    comment: str | None = None
    reviewer: str


class Review(ReviewCreate):
    review_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_id: str
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
