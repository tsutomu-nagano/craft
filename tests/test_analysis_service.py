from app.models.analysis import ResourceFormat
import httpx
import respx

from app.services.analysis import (
    AnalysisService,
    detect_format,
    detect_format_from_headers,
    is_estat_download_url,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload


class FakeMiner:
    def __init__(self):
        self.base_url = "http://miner.test"
        self.extracted_urls = []
        self.converted_urls = []

    async def extract(self, url: str):
        self.extracted_urls.append(url)
        return FakeResponse({"url": url, "sheets": []})

    async def convert(self, url: str):
        self.converted_urls.append(url)
        return FakeResponse({"converted_url": url.replace(".xls", ".xlsx")})


class FakeChecker:
    base_url = "http://checker.test"

    async def check_url(self, url: str):
        return FakeResponse({"url": url, "issues": []})


def test_detect_format_from_url() -> None:
    assert detect_format("https://example.test/data.csv?download=1") == ResourceFormat.CSV
    assert detect_format("https://example.test/book.xls") == ResourceFormat.XLS
    assert detect_format("https://example.test/no-extension") == ResourceFormat.UNKNOWN


def test_detect_format_from_content_disposition() -> None:
    headers = httpx.Headers({"content-disposition": "attachment; filename*=UTF-8''r07sr01.xls"})

    assert detect_format_from_headers(headers) == ResourceFormat.XLS


def test_detect_estat_download_url() -> None:
    assert is_estat_download_url(
        "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0"
    )


@respx.mock
async def test_analyze_estat_download_url_resolves_xls_from_headers() -> None:
    respx.head("https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0").mock(
        return_value=httpx.Response(
            200,
            headers={"content-disposition": "attachment; filename*=UTF-8''r07sr01.xls"},
        )
    )
    miner = FakeMiner()
    service = AnalysisService(miner, FakeChecker())

    result = await service.analyze_table(
        "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0"
    )

    assert result.resource.format == ResourceFormat.XLS
    assert result.structure is not None
    assert miner.extracted_urls == [
        "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0"
    ]
    assert miner.converted_urls == []
    assert result.structure.endpoint == "/api/extract"
    assert result.structure.attempts[0]["endpoint"] == "/api/extract"
    assert result.structure.attempts[0]["request_payload"] == {
        "source": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0"
    }
    assert result.structure.data == {
        "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040387904&fileKind=0",
        "sheets": [],
    }


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
