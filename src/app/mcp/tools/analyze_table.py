from app.dependencies import get_analysis_repository, get_analysis_service


async def analyze_table(url: str) -> dict:
    """Analyze a table resource using miner and checker, then persist the unified result."""
    result = await get_analysis_service().analyze_table(url)
    get_analysis_repository().save(result)
    return result.model_dump(mode="json")
