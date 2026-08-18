from typing import Any

from app.models.analysis import AgentJudgement
from app.repositories.analysis_repository import AnalysisRepository


async def record_agent_judgement(
    analysis_id: str,
    judgement: list[dict[str, Any]],
    reasons: list[str],
    needs_human_review: bool = True,
    model: str | None = None,
    prompt: str | None = None,
    raw_output: str | None = None,
) -> dict[str, Any]:
    """Record an AI judgement produced by the external Chat UI after reviewing an AnalysisResult."""
    agent = AgentJudgement(
        mode="external_chat_ui_recorded",
        model=model,
        judgement=judgement,
        needs_human_review=needs_human_review,
        reasons=reasons,
        prompt=prompt,
        raw_output=raw_output,
    )
    record = AnalysisRepository().update_agent_judgement(analysis_id, agent)
    if record is None:
        return {"ok": False, "error": "analysis not found"}
    return {"ok": True, "analysis_id": analysis_id, "agent": agent.model_dump(mode="json")}
