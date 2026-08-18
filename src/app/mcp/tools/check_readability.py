from app.dependencies import get_analysis_service


async def check_machine_readability(url: str) -> dict:
    """Check CSV, TSV, or Excel machine readability through the checker API."""
    result = await get_analysis_service().check_machine_readability(url)
    return result.model_dump(mode="json")
