from __future__ import annotations

import json
from pathlib import Path
from urllib import error, request

from api.models import AISettings, SummaryResponse


class SummaryService:
    def summarize(self, subtitle_path: str, ai_settings: AISettings) -> SummaryResponse:
        if not subtitle_path:
            raise RuntimeError("当前任务没有可用字幕文件。")
        if not ai_settings.base_url or not ai_settings.api_key or not ai_settings.model:
            raise RuntimeError("请先在设置页配置 AI 服务。")

        content = Path(subtitle_path).read_text(encoding="utf-8", errors="ignore")
        excerpt = content[:12000]

        payload = {
            "model": ai_settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一名视频内容分析助手。"
                        "请基于字幕输出 JSON，字段为 summary、bullets、tags。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "请阅读下面字幕内容，返回中文总结。"
                        "summary 为一段摘要，bullets 为 3-5 条要点，tags 为 3 个简短标签。\n\n"
                        f"{excerpt}"
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
        }

        url = ai_settings.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ai_settings.api_key}",
        }
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"AI 请求失败：{body}") from exc
        except error.URLError as exc:
            raise RuntimeError("AI 服务不可达，请检查 base_url。") from exc

        message = result["choices"][0]["message"]["content"]
        data = json.loads(message)
        return SummaryResponse(
            summary=data.get("summary", ""),
            bullets=data.get("bullets", []),
            tags=data.get("tags", []),
        )
