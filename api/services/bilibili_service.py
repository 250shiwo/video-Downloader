from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from api.models import DownloadItems, ParseResponse
from api.services.task_manager import TaskManager


BVID_PATTERN = re.compile(r"(BV[0-9A-Za-z]{10})")


@dataclass
class BilibiliVideoInfo:
    bvid: str
    cid: int
    title: str
    uploader: str
    duration: int
    thumbnail: str
    webpage_url: str
    part: str


class BilibiliService:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.bilibili.com/",
        }

    def fetch_metadata(self, url: str) -> ParseResponse:
        info = self._load_video_info(url)
        player_info = self._get_player_info(info.bvid, info.cid)
        playurl = self._get_playurl(info.bvid, info.cid)
        subtitles = player_info.get("subtitle", {}).get("subtitles", [])
        formats = [
            description
            for description in playurl.get("accept_description", [])
            if isinstance(description, str)
        ]

        title = info.title if info.part == info.title else f"{info.title} - {info.part}"
        return ParseResponse(
            platform="bilibili",
            title=title,
            uploader=info.uploader,
            duration=info.duration,
            thumbnail=self._normalize_url(info.thumbnail),
            webpage_url=info.webpage_url,
            has_subtitles=bool(subtitles),
            formats=formats[:8],
        )

    def run_download_task(
        self,
        task_id: str,
        url: str,
        items: DownloadItems,
        download_dir: str,
        task_manager: TaskManager,
    ) -> None:
        info = self._load_video_info(url)
        player_info = self._get_player_info(info.bvid, info.cid)
        playurl = self._get_playurl(info.bvid, info.cid)
        target_dir = Path(download_dir).expanduser() / task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_stem = self._safe_name(info.title if info.part == info.title else f"{info.title}-{info.part}")

        task_manager.update_task(task_id, status="running", progress=5)

        if items.video:
            task_manager.append_log(task_id, "下载视频开始")
            video_path = self._download_video(playurl, safe_stem, target_dir)
            task_manager.append_output_file(task_id, str(video_path))
            task_manager.update_task(task_id, progress=40)

        if items.audio:
            task_manager.append_log(task_id, "下载音频开始")
            audio_path = self._download_audio(playurl, safe_stem, target_dir)
            task_manager.append_output_file(task_id, str(audio_path))
            task_manager.update_task(task_id, progress=65)

        if items.subtitles:
            subtitle_path = self._download_subtitle(player_info, safe_stem, target_dir)
            if subtitle_path:
                task_manager.append_log(task_id, "字幕下载完成")
                task_manager.append_output_file(task_id, str(subtitle_path))
                task_manager.update_task(task_id, subtitle_path=str(subtitle_path))
            else:
                task_manager.append_log(task_id, "当前视频没有可用字幕")
            task_manager.update_task(task_id, progress=82)

        if items.thumbnail:
            thumbnail_path = self._download_thumbnail(info.thumbnail, safe_stem, target_dir)
            if thumbnail_path:
                task_manager.append_log(task_id, "封面下载完成")
                task_manager.append_output_file(task_id, str(thumbnail_path))
            task_manager.update_task(task_id, progress=92)

        task_manager.update_task(task_id, status="completed", progress=100)

    def _client(self) -> httpx.Client:
        return httpx.Client(headers=self.headers, follow_redirects=True, timeout=30)

    def _resolve_bvid(self, url: str) -> tuple[str, str]:
        match = BVID_PATTERN.search(url)
        if match:
            return match.group(1), url

        with self._client() as client:
            response = client.get(url)
            response.raise_for_status()
            final_url = str(response.url)

        match = BVID_PATTERN.search(final_url)
        if not match:
            raise RuntimeError("当前 B站 链接无法识别为普通公开视频。")
        return match.group(1), final_url

    def _load_video_info(self, url: str) -> BilibiliVideoInfo:
        bvid, webpage_url = self._resolve_bvid(url)
        parsed_url = urlparse(webpage_url)
        page_number = int(parse_qs(parsed_url.query).get("p", ["1"])[0])

        with self._client() as client:
            response = client.get(
                "https://api.bilibili.com/x/web-interface/view",
                params={"bvid": bvid},
            )
            response.raise_for_status()
            payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(payload.get("message") or "B站 视频信息解析失败。")

        data = payload["data"]
        if data.get("redirect_url") or data.get("is_upower_exclusive") or data.get("is_ugc_pay_preview"):
            raise RuntimeError("当前 B站 链接不是普通公开视频，暂不支持解析下载。")

        pages = data.get("pages") or []
        if not pages:
            raise RuntimeError("当前 B站 视频未返回有效分P信息。")

        index = min(max(page_number - 1, 0), len(pages) - 1)
        page = pages[index]
        return BilibiliVideoInfo(
            bvid=bvid,
            cid=int(page["cid"]),
            title=data.get("title", "未命名视频"),
            uploader=data.get("owner", {}).get("name", "未知UP主"),
            duration=int(page.get("duration") or data.get("duration") or 0),
            thumbnail=data.get("pic", ""),
            webpage_url=webpage_url,
            part=page.get("part") or data.get("title", "未命名视频"),
        )

    def _get_player_info(self, bvid: str, cid: int) -> dict:
        with self._client() as client:
            response = client.get(
                "https://api.bilibili.com/x/player/v2",
                params={"bvid": bvid, "cid": cid},
            )
            response.raise_for_status()
            payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(payload.get("message") or "B站 字幕信息获取失败。")
        return payload["data"]

    def _get_playurl(self, bvid: str, cid: int) -> dict:
        with self._client() as client:
            response = client.get(
                "https://api.bilibili.com/x/player/playurl",
                params={
                    "bvid": bvid,
                    "cid": cid,
                    "fnval": 16,
                    "qn": 64,
                    "fourk": 0,
                },
            )
            response.raise_for_status()
            payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(payload.get("message") or "B站 播放流地址获取失败。")
        return payload["data"]

    def _download_video(self, playurl: dict, safe_stem: str, target_dir: Path) -> Path:
        dash = playurl.get("dash")
        if dash and dash.get("video"):
            ffmpeg = self._ensure_ffmpeg()
            video_stream = self._pick_video_stream(dash["video"])
            audio_stream = self._pick_audio_stream(dash.get("audio", []))
            if not video_stream or not audio_stream:
                raise RuntimeError("B站 未返回可用的音视频流。")

            video_part = target_dir / f"{safe_stem}.video.m4s"
            audio_part = target_dir / f"{safe_stem}.audio.m4s"
            output_file = target_dir / f"{safe_stem}.mp4"
            self._download_file(video_stream["baseUrl"], video_part)
            self._download_file(audio_stream["baseUrl"], audio_part)
            self._merge_streams(ffmpeg, video_part, audio_part, output_file)
            video_part.unlink(missing_ok=True)
            audio_part.unlink(missing_ok=True)
            return output_file

        durl = playurl.get("durl") or []
        if durl:
            output_file = target_dir / f"{safe_stem}.mp4"
            self._download_file(durl[0]["url"], output_file)
            return output_file

        raise RuntimeError("B站 视频流地址缺失，无法下载。")

    def _download_audio(self, playurl: dict, safe_stem: str, target_dir: Path) -> Path:
        ffmpeg = self._ensure_ffmpeg()
        dash = playurl.get("dash")
        if dash and dash.get("audio"):
            audio_stream = self._pick_audio_stream(dash["audio"])
            if not audio_stream:
                raise RuntimeError("B站 未返回可用音频流。")
            raw_audio = target_dir / f"{safe_stem}.source.m4s"
            output_file = target_dir / f"{safe_stem}.m4a"
            self._download_file(audio_stream["baseUrl"], raw_audio)
            self._remux_audio(ffmpeg, raw_audio, output_file)
            raw_audio.unlink(missing_ok=True)
            return output_file

        durl = playurl.get("durl") or []
        if durl:
            source_file = target_dir / f"{safe_stem}.source.mp4"
            output_file = target_dir / f"{safe_stem}.mp3"
            self._download_file(durl[0]["url"], source_file)
            self._extract_audio(ffmpeg, source_file, output_file)
            source_file.unlink(missing_ok=True)
            return output_file

        raise RuntimeError("B站 音频流地址缺失，无法下载。")

    def _download_subtitle(self, player_info: dict, safe_stem: str, target_dir: Path) -> Path | None:
        subtitles = player_info.get("subtitle", {}).get("subtitles", [])
        if not subtitles:
            return None

        subtitle = self._pick_subtitle(subtitles)
        subtitle_url = subtitle.get("subtitle_url")
        if not subtitle_url:
            return None

        with self._client() as client:
            response = client.get(self._normalize_url(subtitle_url))
            response.raise_for_status()
            payload = response.json()

        output_file = target_dir / f"{safe_stem}.srt"
        output_file.write_text(self._subtitle_json_to_srt(payload), encoding="utf-8")
        return output_file

    def _download_thumbnail(self, thumbnail_url: str, safe_stem: str, target_dir: Path) -> Path | None:
        if not thumbnail_url:
            return None
        suffix = Path(urlparse(self._normalize_url(thumbnail_url)).path).suffix or ".jpg"
        output_file = target_dir / f"{safe_stem}{suffix}"
        self._download_file(thumbnail_url, output_file)
        return output_file

    def _download_file(self, url: str, target: Path) -> None:
        normalized_url = self._normalize_url(url)
        with self._client() as client:
            with client.stream("GET", normalized_url) as response:
                response.raise_for_status()
                with target.open("wb") as file_obj:
                    for chunk in response.iter_bytes():
                        file_obj.write(chunk)

    def _merge_streams(self, ffmpeg: str, video_file: Path, audio_file: Path, output_file: Path) -> None:
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(video_file),
                "-i",
                str(audio_file),
                "-c",
                "copy",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "FFmpeg 合并失败。")

    def _remux_audio(self, ffmpeg: str, source_file: Path, output_file: Path) -> None:
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(source_file),
                "-vn",
                "-c",
                "copy",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "音频封装失败。")

    def _extract_audio(self, ffmpeg: str, source_file: Path, output_file: Path) -> None:
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(source_file),
                "-vn",
                "-acodec",
                "libmp3lame",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "音频提取失败。")

    def _ensure_ffmpeg(self) -> str:
        binary = shutil.which("ffmpeg")
        if not binary:
            raise RuntimeError("当前环境未安装 ffmpeg，暂时无法合并或提取 B站 音视频流。")
        return binary

    def _pick_video_stream(self, videos: list[dict]) -> dict | None:
        sorted_streams = sorted(
            videos,
            key=lambda item: (item.get("id", 0), item.get("bandwidth", 0)),
            reverse=True,
        )
        avc_streams = [item for item in sorted_streams if item.get("codecid") == 7]
        return (avc_streams or sorted_streams or [None])[0]

    def _pick_audio_stream(self, audios: list[dict]) -> dict | None:
        if not audios:
            return None
        return sorted(audios, key=lambda item: item.get("bandwidth", 0), reverse=True)[0]

    def _pick_subtitle(self, subtitles: list[dict]) -> dict:
        preferred_patterns = ("zh", "中文", "中")
        for subtitle in subtitles:
            text = f"{subtitle.get('lan', '')} {subtitle.get('lan_doc', '')}"
            if any(pattern in text for pattern in preferred_patterns):
                return subtitle
        return subtitles[0]

    def _subtitle_json_to_srt(self, payload: dict) -> str:
        lines: list[str] = []
        for index, item in enumerate(payload.get("body", []), start=1):
            start = self._format_srt_time(float(item.get("from", 0)))
            end = self._format_srt_time(float(item.get("to", 0)))
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            lines.extend([str(index), f"{start} --> {end}", content, ""])
        return "\n".join(lines).strip() + "\n"

    def _format_srt_time(self, value: float) -> str:
        total_ms = int(value * 1000)
        hours, remainder = divmod(total_ms, 3600 * 1000)
        minutes, remainder = divmod(remainder, 60 * 1000)
        seconds, milliseconds = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _normalize_url(self, url: str) -> str:
        if url.startswith("//"):
            return f"https:{url}"
        return url

    def _safe_name(self, text: str) -> str:
        clean = re.sub(r'[\\\\/:*?"<>|]+', "_", text)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:120] or "bilibili_video"
