from fastapi.testclient import TestClient

from api.main import app
from api.models import AppSettings
from api.services.yt_dlp_service import YtDlpService


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_settings_roundtrip() -> None:
    payload = {
        "download_dir": "./data/downloads",
        "default_items": {
            "video": True,
            "audio": True,
            "subtitles": True,
            "thumbnail": True,
        },
        "ai": {
            "base_url": "https://example.com/v1",
            "api_key": "demo-key",
            "model": "demo-model",
        },
        "browser_cookies": "chrome",
        "cookies_file": "/tmp/cookies.txt",
    }
    save_response = client.put("/api/settings", json=payload)
    assert save_response.status_code == 200

    fetch_response = client.get("/api/settings")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["ai"]["model"] == "demo-model"
    assert fetch_response.json()["browser_cookies"] == "chrome"


def test_parse_rejects_unknown_platform() -> None:
    response = client.post("/api/parse", json={"url": "https://example.com/video/1"})
    assert response.status_code == 400


def test_bilibili_412_error_message_is_more_actionable() -> None:
    service = YtDlpService()
    message = service._normalize_error(
        "bilibili",
        "ERROR: [BiliBili] xxx: Unable to download webpage: HTTP Error 412: Precondition Failed",
    )
    assert "浏览器 Cookie 来源" in message


def test_browser_cookies_precede_cookie_file() -> None:
    service = YtDlpService()
    command = service._base_command(
        "yt-dlp",
        settings=AppSettings(
            browser_cookies="chrome",
            cookies_file="/tmp/cookies.txt",
        ),
        platform="bilibili",
    )
    assert "--cookies-from-browser" in command
    assert "--cookies" not in command
