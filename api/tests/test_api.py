from fastapi.testclient import TestClient

from api.main import app
from api.services.bilibili_service import BilibiliService


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
    }
    save_response = client.put("/api/settings", json=payload)
    assert save_response.status_code == 200

    fetch_response = client.get("/api/settings")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["ai"]["model"] == "demo-model"


def test_parse_rejects_unknown_platform() -> None:
    response = client.post("/api/parse", json={"url": "https://example.com/video/1"})
    assert response.status_code == 400


def test_resolve_bvid_from_direct_url() -> None:
    service = BilibiliService()
    bvid, webpage_url = service._resolve_bvid("https://www.bilibili.com/video/BV1E7wtzaEdq")
    assert bvid == "BV1E7wtzaEdq"
    assert webpage_url.endswith("/BV1E7wtzaEdq")


def test_convert_subtitle_json_to_srt() -> None:
    service = BilibiliService()
    srt = service._subtitle_json_to_srt(
        {
            "body": [
                {"from": 0.0, "to": 2.5, "content": "第一句"},
                {"from": 3.0, "to": 5.0, "content": "第二句"},
            ]
        }
    )
    assert "00:00:00,000 --> 00:00:02,500" in srt
    assert "第一句" in srt


def test_pick_stream_url_supports_multiple_key_shapes() -> None:
    service = BilibiliService()
    assert service._pick_stream_url({"baseUrl": "//example.com/video.m4s"}) == "https://example.com/video.m4s"
    assert service._pick_stream_url({"base_url": "https://example.com/audio.m4s"}) == "https://example.com/audio.m4s"
    assert service._pick_stream_url({"backup_url": ["//example.com/fallback.m4s"]}) == "https://example.com/fallback.m4s"


def test_build_item_ranges_cover_selected_items() -> None:
    service = BilibiliService()
    ranges = service._build_item_ranges(["video", "audio", "thumbnail"])
    assert ranges["video"] == (5, 35)
    assert ranges["audio"] == (35, 65)
    assert ranges["thumbnail"] == (65, 95)
