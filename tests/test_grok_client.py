import os
from types import SimpleNamespace

import pytest

import grok_client
from grok_client import GrokClient


def test_grok_client_requires_api_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.setattr(grok_client, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="GROK_API_KEY"):
        GrokClient()


def test_normalize_role_maps_internal_ai_roles(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    client = GrokClient()

    assert client._normalize_role("model") == "assistant"
    assert client._normalize_role("bot") == "assistant"
    assert client._normalize_role("ai") == "assistant"
    assert client._normalize_role("user") == "user"


@pytest.mark.asyncio
async def test_verify_models_requires_default_model(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    client = GrokClient()

    async def fake_list():
        return SimpleNamespace(data=[SimpleNamespace(id="grok-3-mini")])

    client._client.models.list = fake_list

    assert await client.verify_models() == ["grok-3-mini"]


@pytest.mark.asyncio
async def test_verify_models_raises_when_default_model_missing(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    client = GrokClient()

    async def fake_list():
        return SimpleNamespace(data=[SimpleNamespace(id="grok-3")])

    client._client.models.list = fake_list

    with pytest.raises(RuntimeError, match="grok-3-mini"):
        await client.verify_models()


@pytest.mark.asyncio
async def test_chat_falls_back_to_default_verified_model(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    client = GrokClient()
    client._verified_models = ["grok-3-mini"]
    captured = {}

    async def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
        )

    client._client.chat.completions.create = fake_create

    result = await client.chat(
        [{"role": "model", "content": "hello"}],
        model="unavailable-model",
        stream=False,
    )

    assert result == "ok"
    assert captured["model"] == "grok-3-mini"
    assert captured["messages"] == [{"role": "assistant", "content": "hello"}]
