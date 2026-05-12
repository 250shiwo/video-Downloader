from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from api.models import AppSettings, DownloadItems, ParseResponse
from api.services.link_parser import detect_platform
from api.services.task_manager import TaskManager


class YtDlpService:
    def _base_command(
        self,
        binary: str,
        settings: AppSettings | None = None,
        platform: str | None = None,
    ) -> list[str]:
        command = [binary]
        if settings:
            if settings.browser_cookies.strip():
                command.extend(["--cookies-from-browser", settings.browser_cookies.strip()])
            elif settings.cookies_file.strip():
                command.extend(["--cookies", settings.cookies_file.strip()])

        if platform == "bilibili":
            command.extend(
                [
                    "--add-header",
                    "Referer:https://www.bilibili.com/",
                    "--add-header",
                    (
                        "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/136.0.0.0 Safari/537.36"
                    ),
                ]
            )

        return command

    def _normalize_error(self, platform: str, stderr: str) -> str:
        message = stderr.strip() or "解析失败，请检查链接是否可访问。"
        lowered = message.lower()
        if platform == "bilibili" and "http error 412" in lowered:
            return (
                "B站返回 412 风控校验失败。请先在设置页填写“浏览器 Cookie 来源”"
                "（例如 chrome、edge、firefox），并确保对应浏览器里已经登录 B站，再重试。"
            )
        return message

    def ensure_binary(self) -> str:
        binary = shutil.which("yt-dlp")
        if not binary:
            raise RuntimeError("未检测到 yt-dlp，请先在本机安装 yt-dlp 后再使用下载能力。")
        return binary

    def fetch_metadata(self, url: str, settings: AppSettings | None = None) -> ParseResponse:
        platform = detect_platform(url)
        binary = self.ensure_binary()
        command = self._base_command(binary, settings=settings, platform=platform)
        result = subprocess.run(
            [*command, "--dump-single-json", "--skip-download", url],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = self._normalize_error(platform, result.stderr)
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
        platform = detect_platform(url)
        task_manager.update_task(task_id, status="running", progress=5)

        target_dir = Path(settings.download_dir).expanduser() / task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(target_dir / "%(title).120B.%(ext)s")
        base_command = self._base_command(binary, settings=settings, platform=platform)

        steps: list[tuple[str, list[str], int]] = []
        if items.video:
            steps.append(
                (
                    "下载视频",
                    [*base_command, "-o", output_template, url],
                    35,
                )
            )
        if items.audio:
            steps.append(
                (
                    "提取音频",
                    [*base_command, "-x", "--audio-format", "mp3", "-o", output_template, url],
                    60,
                )
            )
        if items.subtitles:
            steps.append(
                (
                    "下载字幕",
                    [
                        *base_command,
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
                    [
                        *base_command,
                        "--skip-download",
                        "--write-thumbnail",
                        "-o",
                        output_template,
                        url,
                    ],
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
                raise RuntimeError(
                    f"{label}失败：{self._normalize_error(platform, result.stderr)}"
                )
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
