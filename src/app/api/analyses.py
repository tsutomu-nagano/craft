from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_analysis_repository, get_analysis_service
from app.models.analysis import AnalysisRequest, AnalysisResult
from app.models.review import Review, ReviewCreate
from app.repositories.analysis_repository import AnalysisRepository
from app.services.analysis import AnalysisService
from app.services.review import ReviewService
from app.dependencies import get_review_service

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


@router.get("")
def list_analyses(repository: AnalysisRepository = Depends(get_analysis_repository)) -> list[dict]:
    return [
        {
            "analysis_id": item.analysis_id,
            "target_url": item.target_url,
            "file_format": item.file_format,
            "status": item.status,
            "created_at": item.created_at,
        }
        for item in repository.list()
    ]


@router.post("", response_model=AnalysisResult)
async def create_analysis(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> AnalysisResult:
    result = await service.analyze_table(request.url)
    return repository.save(result)


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: str,
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> dict:
    item = repository.get(analysis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="analysis not found")
    return {
        "analysis_id": item.analysis_id,
        "resource": {"url": item.target_url, "format": item.file_format},
        "structure": item.miner_result,
        "readability": item.checker_result,
        "agent": item.agent_result,
        "skill_versions": item.skill_versions,
        "status": item.status,
        "created_at": item.created_at,
    }


@router.post("/{analysis_id}/reviews", response_model=Review)
def create_review(
    analysis_id: str,
    request: ReviewCreate,
    service: ReviewService = Depends(get_review_service),
) -> Review:
    return service.create(analysis_id, request)
