from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.repositories.database as database
import app.repositories.review_repository as review_repository_module
from app.models.review import Review, ReviewDecision, ReviewUpdate
from app.repositories.database import Base
from app.repositories.review_repository import ReviewRepository


def test_update_review(tmp_path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    database.SessionLocal = testing_session
    review_repository_module.SessionLocal = testing_session

    repository = ReviewRepository()
    review = Review(
        analysis_id="analysis-1",
        target_issue="issue-1",
        human_decision=ReviewDecision.APPROVED,
        reviewer="reviewer",
        reviewed_at=datetime.now(timezone.utc),
    )
    repository.save(review)

    updated = repository.update(
        review.review_id,
        ReviewUpdate(human_decision=ReviewDecision.NEEDS_INVESTIGATION, reason="要確認"),
    )

    assert updated is not None
    assert updated.human_decision == ReviewDecision.NEEDS_INVESTIGATION
    assert updated.reason == "要確認"
