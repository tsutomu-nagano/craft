from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.repositories.analysis_repository as analysis_repository_module
import app.repositories.database as database
import app.repositories.review_repository as review_repository_module
from app.models.analysis import AnalysisResource, AnalysisResult, ResourceFormat
from app.models.review import Review, ReviewDecision
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.database import Base
from app.repositories.review_repository import ReviewRepository


def test_delete_analysis_also_deletes_reviews(tmp_path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    database.SessionLocal = testing_session
    analysis_repository_module.SessionLocal = testing_session
    review_repository_module.SessionLocal = testing_session

    analysis_repository = AnalysisRepository()
    review_repository = ReviewRepository()
    analysis = AnalysisResult(
        resource=AnalysisResource(url="https://example.test/table.csv", format=ResourceFormat.CSV),
        created_at=datetime.now(timezone.utc),
    )
    review = Review(
        analysis_id=analysis.analysis_id,
        target_issue="issue-1",
        human_decision=ReviewDecision.APPROVED,
        reviewer="reviewer",
        reviewed_at=datetime.now(timezone.utc),
    )

    analysis_repository.save(analysis)
    review_repository.save(review)

    assert analysis_repository.delete(analysis.analysis_id) is True
    assert analysis_repository.get(analysis.analysis_id) is None
    assert review_repository.list_by_analysis(analysis.analysis_id) == []
