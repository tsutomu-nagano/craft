from app.models.analysis import AnalysisResult
from app.repositories.database import AnalysisRecord, SessionLocal


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
