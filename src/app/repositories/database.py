from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    analysis_id: Mapped[str] = mapped_column(String, primary_key=True)
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    file_format: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    miner_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    checker_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    agent_result: Mapped[dict] = mapped_column(JSON, nullable=False)
    skill_versions: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)


class ReviewRecord(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    analysis_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_issue: Mapped[str] = mapped_column(String, nullable=False)
    ai_judgement: Mapped[str | None] = mapped_column(String, nullable=True)
    human_decision: Mapped[str] = mapped_column(String, nullable=False)
    corrected_content: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewer: Mapped[str] = mapped_column(String, nullable=False)
    reviewed_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
