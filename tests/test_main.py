from fastapi.testclient import TestClient

import main


class FakeGrokClient:
    async def verify_models(self):
        return ["grok-3-mini"]

    async def health_check(self):
        return True

    async def close(self):
        return None


def test_app_boots_and_health_responds(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["grok"] is True
