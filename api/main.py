from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    AppSettings,
    DownloadRequest,
    DownloadTaskResponse,
    ParseRequest,
    ParseResponse,
    SummaryRequest,
    SummaryResponse,
    TaskDetail,
    TaskSummary,
)
from api.services.config_service import ConfigService
from api.services.task_manager import TaskManager
from api.services.yt_dlp_service import YtDlpService
from api.services.summary_service import SummaryService

app = FastAPI(title="Video Downloader AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)
config_service = ConfigService()
task_manager = TaskManager()
yt_dlp_service = YtDlpService()
summary_service = SummaryService()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse", response_model=ParseResponse)
def parse_video(payload: ParseRequest) -> ParseResponse:
    try:
        settings = config_service.get_settings()
        return yt_dlp_service.fetch_metadata(payload.url, settings=settings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/tasks/download", response_model=DownloadTaskResponse)
def create_download_task(payload: DownloadRequest) -> DownloadTaskResponse:
    settings = config_service.get_settings()
    try:
        metadata = yt_dlp_service.fetch_metadata(payload.url, settings=settings)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    task_id = uuid4().hex[:12]
    task_manager.create_task(task_id, metadata.title, payload.url)

    def worker() -> None:
        try:
            yt_dlp_service.run_download_task(
                task_id=task_id,
                url=payload.url,
                items=payload.items,
                settings=settings,
                task_manager=task_manager,
            )
        except RuntimeError as exc:
            task_manager.append_log(task_id, str(exc))
            task_manager.update_task(
                task_id,
                status="failed",
                error=str(exc),
                progress=100,
            )

    executor.submit(worker)
    return DownloadTaskResponse(task_id=task_id, status="queued")


@app.get("/api/tasks", response_model=list[TaskSummary])
def list_tasks() -> list[TaskSummary]:
    return task_manager.list_tasks()


@app.get("/api/tasks/{task_id}", response_model=TaskDetail)
def get_task(task_id: str) -> TaskDetail:
    try:
        return task_manager.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="任务不存在。") from exc


@app.get("/api/settings", response_model=AppSettings)
def get_settings() -> AppSettings:
    return config_service.get_settings()


@app.put("/api/settings", response_model=AppSettings)
def update_settings(payload: AppSettings) -> AppSettings:
    return config_service.save_settings(payload)


@app.post("/api/summary", response_model=SummaryResponse)
def summarize(payload: SummaryRequest) -> SummaryResponse:
    try:
        task = task_manager.get_task(payload.task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="任务不存在。") from exc

    try:
        settings = config_service.get_settings()
        return summary_service.summarize(task.subtitle_path or "", settings.ai)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
