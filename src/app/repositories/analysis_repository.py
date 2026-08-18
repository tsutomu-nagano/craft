from __future__ import annotations

from app.models.analysis import AgentJudgement, AnalysisResult
from app.repositories.database import AnalysisRecord, SessionLocal
from app.repositories.review_repository import ReviewRepository


class AnalysisRepository:
    def save(self, analysis: AnalysisResult) -> AnalysisResult:
        with SessionLocal() as session:
            record = AnalysisRecord(
                analysis_id=analysis.analysis_id,
                target_url=analysis.resource.url,
                file_format=analysis.resource.format.value,
                status=analysis.status.value,
                miner_result=analysis.structure.model_dump(mode="json") if analysis.structure else None,
                checker_result=analysis.readability.model_dump(mode="json") if analysis.readability else None,
                agent_result=analysis.agent.model_dump(mode="json"),
                skill_versions=analysis.skill_versions,
                created_at=analysis.created_at,
            )
            session.merge(record)
            session.commit()
        return analysis

    def list(self) -> list[AnalysisRecord]:
        with SessionLocal() as session:
            return list(session.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all())

    def get(self, analysis_id: str) -> AnalysisRecord | None:
        with SessionLocal() as session:
            return session.get(AnalysisRecord, analysis_id)

    def delete(self, analysis_id: str) -> bool:
        ReviewRepository().delete_by_analysis(analysis_id)
        with SessionLocal() as session:
            record = session.get(AnalysisRecord, analysis_id)
            if record is None:
                return False
            session.delete(record)
            session.commit()
            return True

    def update_agent_judgement(
        self,
        analysis_id: str,
        judgement: AgentJudgement,
    ) -> AnalysisRecord | None:
        with SessionLocal() as session:
            record = session.get(AnalysisRecord, analysis_id)
            if record is None:
                return None
            record.agent_result = judgement.model_dump(mode="json")
            session.commit()
            session.refresh(record)
            return record
