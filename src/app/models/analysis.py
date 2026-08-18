from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ResourceFormat(StrEnum):
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"
    TSV = "tsv"
    UNKNOWN = "unknown"


class AnalysisStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    NEEDS_INVESTIGATION = "needs_investigation"


class ApiExecution(BaseModel):
    source: str
    ok: bool
    api_base_url: str | None = None
    endpoint: str | None = None
    method: str | None = None
    request_url: str | None = None
    attempts: list[dict[str, Any]] = Field(default_factory=list)
    data: dict[str, Any] | None = None
    error: str | None = None


class AnalysisResource(BaseModel):
    url: str
    format: ResourceFormat = ResourceFormat.UNKNOWN


class AgentJudgement(BaseModel):
    judgement: list[dict[str, Any]] = Field(default_factory=list)
    needs_human_review: bool = True
    reasons: list[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    url: str


class AnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    resource: AnalysisResource
    structure: ApiExecution | None = None
    readability: ApiExecution | None = None
    agent: AgentJudgement = Field(default_factory=AgentJudgement)
    skill_versions: dict[str, str] = Field(default_factory=dict)
    status: AnalysisStatus = AnalysisStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
