from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["queued", "running", "completed", "failed"]


class DownloadItems(BaseModel):
    video: bool = True
    audio: bool = True
    subtitles: bool = True
    thumbnail: bool = True


class AISettings(BaseModel):
    base_url: str = ""
    api_key: str = ""
    model: str = ""


class AppSettings(BaseModel):
    download_dir: str = "./data/downloads"
    default_items: DownloadItems = Field(default_factory=DownloadItems)
    ai: AISettings = Field(default_factory=AISettings)


class ParseRequest(BaseModel):
    url: str


class ParseResponse(BaseModel):
    platform: str
    title: str
    uploader: str | None = None
    duration: int | None = None
    thumbnail: str | None = None
    webpage_url: str
    has_subtitles: bool = False
    formats: list[str] = Field(default_factory=list)


class DownloadRequest(BaseModel):
    url: str
    items: DownloadItems


class DownloadTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus


class SummaryRequest(BaseModel):
    task_id: str


class SummaryResponse(BaseModel):
    summary: str
    bullets: list[str]
    tags: list[str]


class TaskSummary(BaseModel):
    id: str
    title: str
    status: TaskStatus
    progress: int
    created_at: str


class TaskDetail(TaskSummary):
    url: str
    logs: list[str] = Field(default_factory=list)
    output_files: list[str] = Field(default_factory=list)
    error: str | None = None
    subtitle_path: str | None = None
