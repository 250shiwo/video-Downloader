from fastapi.testclient import TestClient

from api.main import app


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
