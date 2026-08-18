from app.dependencies import get_analysis_service


async def extract_excel_metadata(url: str) -> dict:
    """Extract Excel structure and metadata through the miner API."""
    result = await get_analysis_service().extract_excel_metadata(url)
    return result.model_dump(mode="json")
