from __future__ import annotations

from urllib.parse import urlparse


PLATFORM_RULES = {
    "bilibili": ("bilibili.com", "b23.tv"),
    "youtube": ("youtube.com", "youtu.be"),
    "tiktok": ("tiktok.com",),
    "douyin": ("douyin.com", "iesdouyin.com"),
}


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if not host:
        raise ValueError("链接格式无效，请输入完整的视频链接。")

    for platform, hosts in PLATFORM_RULES.items():
        if any(domain in host for domain in hosts):
            return platform

    raise ValueError("当前链接不在支持的平台范围内。")
