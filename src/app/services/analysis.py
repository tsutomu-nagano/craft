from email.message import Message
from pathlib import PurePosixPath

import httpx

from app.clients.machine_readable_checker import MachineReadableCheckerClient
from app.clients.miner import MinerClient
from app.models.analysis import (
    AgentJudgement,
    AnalysisResource,
    AnalysisResult,
    ApiExecution,
    ResourceFormat,
)


def detect_format(url: str) -> ResourceFormat:
    suffix = PurePosixPath(url.split("?", 1)[0]).suffix.lower().lstrip(".")
    return detect_format_from_suffix(suffix)


def is_estat_download_url(url: str) -> bool:
    return "e-stat.go.jp/stat-search/file-download" in url


def detect_format_from_suffix(suffix: str) -> ResourceFormat:
    try:
        return ResourceFormat(suffix)
    except ValueError:
        return ResourceFormat.UNKNOWN


def detect_format_from_headers(headers: httpx.Headers) -> ResourceFormat:
    disposition = headers.get("content-disposition")
    if disposition:
        message = Message()
        message["content-disposition"] = disposition
        filename = message.get_filename()
        if filename:
            detected = detect_format(filename)
            if detected != ResourceFormat.UNKNOWN:
                return detected

    content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    return {
        "text/csv": ResourceFormat.CSV,
        "text/tab-separated-values": ResourceFormat.TSV,
        "application/vnd.ms-excel": ResourceFormat.XLS,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ResourceFormat.XLSX,
    }.get(content_type, ResourceFormat.UNKNOWN)


class AnalysisService:
    def __init__(
        self,
        miner: MinerClient,
        checker: MachineReadableCheckerClient,
    ) -> None:
        self.miner = miner
        self.checker = checker

    async def analyze_table(self, url: str) -> AnalysisResult:
        resource_format = await self._resolve_format(url)
        result = AnalysisResult(resource=AnalysisResource(url=url, format=resource_format))

        if resource_format in {ResourceFormat.XLS, ResourceFormat.XLSX}:
            result.structure = await self._run_miner(url, convert_first=resource_format == ResourceFormat.XLS)

        if resource_format in {ResourceFormat.XLS, ResourceFormat.XLSX, ResourceFormat.CSV, ResourceFormat.TSV}:
            result.readability = await self._run_checker(url)

        result.agent = self._judge(result)
        result.skill_versions = {"machine-readability": "0.1.0"}
        return result

    async def extract_excel_metadata(self, url: str) -> ApiExecution:
        resource_format = await self._resolve_format(url)
        return await self._run_miner(url, convert_first=resource_format == ResourceFormat.XLS)

    async def check_machine_readability(self, url: str) -> ApiExecution:
        return await self._run_checker(url)

    async def _resolve_format(self, url: str) -> ResourceFormat:
        resource_format = detect_format(url)
        if resource_format != ResourceFormat.UNKNOWN:
            return resource_format

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.head(url)
                response.raise_for_status()
                resource_format = detect_format_from_headers(response.headers)
                if resource_format != ResourceFormat.UNKNOWN:
                    return resource_format
        except httpx.HTTPError:
            pass

        if is_estat_download_url(url):
            return ResourceFormat.XLS

        return ResourceFormat.UNKNOWN

    async def _run_miner(self, url: str, convert_first: bool = False) -> ApiExecution:
        attempts: list[dict[str, object]] = []
        try:
            response = await self.miner.extract(url)
            request_payload = {"source": url}
            attempts.append(
                self._attempt(
                    source="miner",
                    endpoint="/api/extract",
                    method="POST",
                    request_payload=request_payload,
                    ok=True,
                )
            )
            return ApiExecution(
                source="miner",
                ok=True,
                api_base_url=self.miner.base_url,
                endpoint="/api/extract",
                method="POST",
                request_url=url,
                attempts=attempts,
                data=response.payload,
            )
        except (httpx.HTTPError, ValueError) as exc:
            attempts.append(
                self._attempt(
                    source="miner",
                    endpoint="/api/extract",
                    method="POST",
                    request_payload={"source": url},
                    ok=False,
                    error=exc,
                )
            )
            return ApiExecution(
                source="miner",
                ok=False,
                api_base_url=self.miner.base_url,
                endpoint="/api/extract",
                method="POST",
                request_url=url,
                attempts=attempts,
                error=f"{type(exc).__name__}: {exc}",
            )

    async def _run_checker(self, url: str) -> ApiExecution:
        try:
            response = await self.checker.check_url(url)
            return ApiExecution(
                source="machine-readable-checker",
                ok=True,
                api_base_url=self.checker.base_url,
                endpoint="/api/check-url",
                method="POST",
                request_url=url,
                attempts=[
                    self._attempt(
                    source="machine-readable-checker",
                    endpoint="/api/check-url",
                    method="POST",
                    request_payload={"url": url},
                    ok=True,
                )
            ],
                data=response.payload,
            )
        except (httpx.HTTPError, ValueError) as exc:
            return ApiExecution(
                source="machine-readable-checker",
                ok=False,
                api_base_url=self.checker.base_url,
                endpoint="/api/check-url",
                method="POST",
                request_url=url,
                attempts=[
                    self._attempt(
                        source="machine-readable-checker",
                        endpoint="/api/check-url",
                        method="POST",
                        request_payload={"url": url},
                        ok=False,
                        error=exc,
                    )
                ],
                error=f"{type(exc).__name__}: {exc}",
            )

    def _attempt(
        self,
        source: str,
        endpoint: str,
        method: str,
        request_payload: dict[str, str],
        ok: bool,
        error: Exception | None = None,
    ) -> dict[str, object]:
        return {
            "source": source,
            "api_base_url": self.miner.base_url if source == "miner" else self.checker.base_url,
            "endpoint": endpoint,
            "method": method,
            "request_payload": request_payload,
            "ok": ok,
            "error": f"{type(error).__name__}: {error}" if error else None,
        }

    def _judge(self, result: AnalysisResult) -> AgentJudgement:
        reasons: list[str] = []
        if result.structure and not result.structure.ok:
            reasons.append("minerの解析に失敗したため人による確認が必要です。")
        if result.readability and not result.readability.ok:
            reasons.append("machine-readable-checkerの解析に失敗したため人による確認が必要です。")
        if result.resource.format == ResourceFormat.UNKNOWN:
            reasons.append("ファイル形式を判定できませんでした。")
        if not reasons:
            reasons.append("初期MVPではAI判断を確定せず、人による確認対象として保存します。")
        return AgentJudgement(judgement=[], needs_human_review=True, reasons=reasons)
