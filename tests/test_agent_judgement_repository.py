from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.repositories.analysis_repository as analysis_repository_module
import app.repositories.database as database
import app.repositories.review_repository as review_repository_module
from app.models.analysis import AgentJudgement, AnalysisResource, AnalysisResult, ResourceFormat
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.database import Base


def test_update_agent_judgement(tmp_path) -> None:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    database.SessionLocal = testing_session
    analysis_repository_module.SessionLocal = testing_session
    review_repository_module.SessionLocal = testing_session

    repository = AnalysisRepository()
    analysis = AnalysisResult(
        resource=AnalysisResource(url="https://example.test/table.csv", format=ResourceFormat.CSV),
        created_at=datetime.now(timezone.utc),
    )
    repository.save(analysis)

    updated = repository.update_agent_judgement(
        analysis.analysis_id,
        AgentJudgement(
            mode="external_chat_ui_recorded",
            model="chat-ui",
            judgement=[{"code": "header", "message": "項目名を確認"}],
            reasons=["Chat UI上のAIが判断案を作成しました。"],
        ),
    )

    assert updated is not None
    assert updated.agent_result["mode"] == "external_chat_ui_recorded"
    assert updated.agent_result["judgement"][0]["code"] == "header"
