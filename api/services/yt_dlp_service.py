from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from api.models import AppSettings, DownloadItems, ParseResponse
from api.services.link_parser import detect_platform
from api.services.task_manager import TaskManager


class YtDlpService:
    def ensure_binary(self) -> str:
        binary = shutil.which("yt-dlp")
        if not binary:
            raise RuntimeError("未检测到 yt-dlp，请先在本机安装 yt-dlp 后再使用下载能力。")
        return binary

    def fetch_metadata(self, url: str) -> ParseResponse:
        platform = detect_platform(url)
        binary = self.ensure_binary()
        result = subprocess.run(
            [binary, "--dump-single-json", "--skip-download", url],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or "解析失败，请检查链接是否可访问。"
            raise RuntimeError(message)

        payload = json.loads(result.stdout)
        subtitles = payload.get("subtitles") or {}
        auto_subtitles = payload.get("automatic_captions") or {}
        format_names = []
        for item in payload.get("formats", [])[:8]:
            ext = item.get("ext", "unknown")
            note = item.get("format_note") or item.get("resolution") or "source"
            format_names.append(f"{ext} · {note}")

        return ParseResponse(
            platform=platform,
            title=payload.get("title", "未命名视频"),
            uploader=payload.get("uploader") or payload.get("channel"),
            duration=payload.get("duration"),
            thumbnail=payload.get("thumbnail"),
            webpage_url=payload.get("webpage_url") or url,
            has_subtitles=bool(subtitles or auto_subtitles),
            formats=format_names,
        )

    def run_download_task(
        self,
        task_id: str,
        url: str,
        items: DownloadItems,
        settings: AppSettings,
        task_manager: TaskManager,
    ) -> None:
        binary = self.ensure_binary()
        task_manager.update_task(task_id, status="running", progress=5)

        target_dir = Path(settings.download_dir).expanduser() / task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(target_dir / "%(title).120B.%(ext)s")

        steps: list[tuple[str, list[str], int]] = []
        if items.video:
            steps.append(
                (
                    "下载视频",
                    [binary, "-o", output_template, url],
                    35,
                )
            )
        if items.audio:
            steps.append(
                (
                    "提取音频",
                    [binary, "-x", "--audio-format", "mp3", "-o", output_template, url],
                    60,
                )
            )
        if items.subtitles:
            steps.append(
                (
                    "下载字幕",
                    [
                        binary,
                        "--skip-download",
                        "--write-subs",
                        "--write-auto-subs",
                        "--sub-langs",
                        "all",
                        "--convert-subs",
                        "srt",
                        "-o",
                        output_template,
                        url,
                    ],
                    80,
                )
            )
        if items.thumbnail:
            steps.append(
                (
                    "下载封面",
                    [binary, "--skip-download", "--write-thumbnail", "-o", output_template, url],
                    90,
                )
            )

        if not steps:
            raise RuntimeError("请至少选择一个下载项。")

        for label, command, progress in steps:
            task_manager.append_log(task_id, f"{label}开始")
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            output = (result.stdout + "\n" + result.stderr).strip()
            if output:
                for line in output.splitlines()[-12:]:
                    task_manager.append_log(task_id, line)
            if result.returncode != 0:
                raise RuntimeError(f"{label}失败：{result.stderr.strip() or '未知错误'}")
            task_manager.update_task(task_id, progress=progress)

        subtitle_path = self._find_first(target_dir, {".srt", ".vtt", ".ass"})
        if subtitle_path:
            task_manager.update_task(task_id, subtitle_path=str(subtitle_path))

        for file_path in sorted(target_dir.glob("*")):
            task_manager.append_output_file(task_id, str(file_path))

        task_manager.update_task(task_id, status="completed", progress=100)

    def _find_first(self, directory: Path, suffixes: set[str]) -> Path | None:
        for file_path in sorted(directory.glob("*")):
            if file_path.suffix.lower() in suffixes:
                return file_path
        return None
