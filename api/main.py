from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

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


@app.get("/api/files")
def download_file(path: str = Query(..., description="任务生成文件的绝对或相对路径")) -> FileResponse:
    settings = config_service.get_settings()
    requested = Path(path).expanduser()
    if not requested.is_absolute():
        requested = Path.cwd() / requested

    downloads_root = Path(settings.download_dir).expanduser().resolve()
    requested = requested.resolve()

    if downloads_root not in requested.parents:
        raise HTTPException(status_code=400, detail="文件路径不在允许的下载目录内。")
    if not requested.exists() or not requested.is_file():
        raise HTTPException(status_code=404, detail="文件不存在。")

    return FileResponse(path=requested, filename=requested.name)


@app.get("/api/proxy-image")
def proxy_image(url: str = Query(..., description="远程图片地址")) -> Response:
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="图片地址无效。")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
    }
    if "hdslb.com" in url or "bilibili.com" in url:
        headers["Referer"] = "https://www.bilibili.com/"

    try:
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="封面加载失败。") from exc

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=3600"},
    )
