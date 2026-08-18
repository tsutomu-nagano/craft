from app.models.analysis import ResourceFormat
from app.services.analysis import AnalysisService, detect_format


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload


class FakeMiner:
    async def extract(self, url: str):
        return FakeResponse({"url": url, "sheets": []})

    async def convert(self, url: str):
        return FakeResponse({"converted_url": url.replace(".xls", ".xlsx")})


class FakeChecker:
    async def check_url(self, url: str):
        return FakeResponse({"url": url, "issues": []})


def test_detect_format_from_url() -> None:
    assert detect_format("https://example.test/data.csv?download=1") == ResourceFormat.CSV
    assert detect_format("https://example.test/book.xls") == ResourceFormat.XLS
    assert detect_format("https://example.test/no-extension") == ResourceFormat.UNKNOWN


async def test_analyze_xlsx_runs_miner_and_checker() -> None:
    service = AnalysisService(FakeMiner(), FakeChecker())

    result = await service.analyze_table("https://example.test/book.xlsx")

    assert result.resource.format == ResourceFormat.XLSX
    assert result.structure is not None
    assert result.structure.source == "miner"
    assert result.structure.ok is True
    assert result.readability is not None
    assert result.readability.source == "machine-readable-checker"
    assert result.agent.needs_human_review is True


async def test_analyze_csv_skips_miner() -> None:
    service = AnalysisService(FakeMiner(), FakeChecker())

    result = await service.analyze_table("https://example.test/table.csv")

    assert result.resource.format == ResourceFormat.CSV
    assert result.structure is None
    assert result.readability is not None
