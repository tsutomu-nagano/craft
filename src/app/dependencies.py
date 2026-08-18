from app.clients.machine_readable_checker import MachineReadableCheckerClient
from app.clients.miner import MinerClient
from app.config import settings
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.review_repository import ReviewRepository
from app.services.analysis import AnalysisService
from app.services.review import ReviewService


def get_analysis_service() -> AnalysisService:
    return AnalysisService(
        miner=MinerClient(str(settings.miner_api_base_url), settings.api_timeout_seconds),
        checker=MachineReadableCheckerClient(
            str(settings.machine_readable_checker_api_base_url),
            settings.api_timeout_seconds,
        ),
    )


def get_analysis_repository() -> AnalysisRepository:
    return AnalysisRepository()


def get_review_service() -> ReviewService:
    return ReviewService(ReviewRepository())
