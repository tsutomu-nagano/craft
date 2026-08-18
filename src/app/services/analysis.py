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
    try:
        return ResourceFormat(suffix)
    except ValueError:
        return ResourceFormat.UNKNOWN


class AnalysisService:
    def __init__(
        self,
        miner: MinerClient,
        checker: MachineReadableCheckerClient,
    ) -> None:
        self.miner = miner
        self.checker = checker

    async def analyze_table(self, url: str) -> AnalysisResult:
        resource_format = detect_format(url)
        result = AnalysisResult(resource=AnalysisResource(url=url, format=resource_format))

        if resource_format in {ResourceFormat.XLS, ResourceFormat.XLSX}:
            result.structure = await self._run_miner(url, convert_first=resource_format == ResourceFormat.XLS)

        if resource_format in {ResourceFormat.XLS, ResourceFormat.XLSX, ResourceFormat.CSV, ResourceFormat.TSV}:
            result.readability = await self._run_checker(url)

        result.agent = self._judge(result)
        result.skill_versions = {"machine-readability": "0.1.0"}
        return result

    async def extract_excel_metadata(self, url: str) -> ApiExecution:
        return await self._run_miner(url, convert_first=detect_format(url) == ResourceFormat.XLS)

    async def check_machine_readability(self, url: str) -> ApiExecution:
        return await self._run_checker(url)

    async def _run_miner(self, url: str, convert_first: bool = False) -> ApiExecution:
        try:
            if convert_first:
                converted = await self.miner.convert(url)
                url = str(converted.payload.get("url") or converted.payload.get("converted_url") or url)
            response = await self.miner.extract(url)
            return ApiExecution(source="miner", ok=True, data=response.payload)
        except (httpx.HTTPError, ValueError) as exc:
            return ApiExecution(source="miner", ok=False, error=str(exc))

    async def _run_checker(self, url: str) -> ApiExecution:
        try:
            response = await self.checker.check_url(url)
            return ApiExecution(source="machine-readable-checker", ok=True, data=response.payload)
        except (httpx.HTTPError, ValueError) as exc:
            return ApiExecution(source="machine-readable-checker", ok=False, error=str(exc))

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
