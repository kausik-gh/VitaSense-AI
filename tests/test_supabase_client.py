import pytest

import db.supabase_client as supabase_client


def test_get_supabase_requires_url_and_service_role_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setattr(supabase_client, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        supabase_client.get_supabase()


def test_get_supabase_uses_environment_values(monkeypatch):
    created = {}

    def fake_create_client(url, key):
        created["url"] = url
        created["key"] = key
        return object()

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setattr(supabase_client, "create_client", fake_create_client)

    client = supabase_client.get_supabase()

    assert client is not None
    assert created == {
        "url": "https://example.supabase.co",
        "key": "service-role-key",
    }
