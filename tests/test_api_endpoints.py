from types import SimpleNamespace

from fastapi.testclient import TestClient

import main


class FakeGrokClient:
    async def verify_models(self):
        return ["grok-3-mini"]

    async def health_check(self):
        return True

    async def close(self):
        return None


class FakeQuery:
    def __init__(self, calls):
        self.calls = calls

    def select(self, columns):
        self.calls.append(("select", columns))
        return self

    def eq(self, column, value):
        self.calls.append(("eq", column, value))
        return self

    def order(self, column, desc=False):
        self.calls.append(("order", column, desc))
        return self

    def limit(self, value):
        self.calls.append(("limit", value))
        return self

    def maybe_single(self):
        self.calls.append(("maybe_single",))
        return self

    def upsert(self, payload, *, on_conflict=""):
        self.calls.append(("upsert", payload, on_conflict))
        return self

    def execute(self):
        self.calls.append(("execute",))
        return SimpleNamespace(
            data=[
                {
                    "user_id": 9,
                    "session_id": "abc",
                    "message_role": "assistant",
                    "message_content": "hello",
                }
            ]
        )


class FakeSupabase:
    def __init__(self):
        self.calls = []

    def table(self, table_name):
        self.calls.append(("table", table_name))
        return FakeQuery(self.calls)


class EmptyQuery(FakeQuery):
    def execute(self):
        self.calls.append(("execute",))
        return SimpleNamespace(data=None)


class EmptySupabase(FakeSupabase):
    def table(self, table_name):
        self.calls.append(("table", table_name))
        return EmptyQuery(self.calls)


async def fake_stream_chat_sse(user_id, session_id, user_message, *, dependencies):
    yield "data: streamed\n\n"
    yield "data: [DONE]\n\n"


def test_chat_endpoint_streams_sse_and_done(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    monkeypatch.setattr(main, "stream_chat_sse", fake_stream_chat_sse)

    with TestClient(main.app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"user_id": 1, "session_id": "abc", "message": "I feel tired"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data: streamed" in response.text
    assert "data: [DONE]" in response.text


def test_chat_endpoint_rejects_empty_message(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"user_id": 1, "message": "   "},
        )

    assert response.status_code == 422


def test_chat_endpoint_rejects_invalid_user_id(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"user_id": 0, "message": "hello"},
        )

    assert response.status_code == 422


def test_history_endpoint_filters_by_user_id_first(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    supabase = FakeSupabase()
    monkeypatch.setattr(main, "get_supabase", lambda: supabase)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/9/history?limit=10")

    assert response.status_code == 200
    assert response.json()["history"][0]["user_id"] == 9

    filter_calls = [
        call for call in supabase.calls if call[0] in {"eq", "order", "limit"}
    ]
    assert supabase.calls[0] == ("table", "chatbot_conversation_history")
    assert filter_calls[0] == ("eq", "user_id", 9)
    assert ("order", "created_at", True) in supabase.calls
    assert ("limit", 10) in supabase.calls


def test_history_endpoint_normalizes_empty_storage_response(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    monkeypatch.setattr(main, "get_supabase", lambda: EmptySupabase())

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/9/history")

    assert response.status_code == 200
    assert response.json() == {"history": []}


def test_history_endpoint_rejects_invalid_limit(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/9/history?limit=101")

    assert response.status_code == 422


def test_history_endpoint_handles_storage_unavailable(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    def fail_supabase():
        raise RuntimeError("missing env")

    monkeypatch.setattr(main, "get_supabase", fail_supabase)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/9/history")

    assert response.status_code == 503


def test_wellness_forecast_endpoint_returns_structured_forecast(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    monkeypatch.setattr(main, "get_supabase", lambda: object())

    async def fake_profile(supabase, user_id):
        return {
            "user_medical_identity": {
                "allergy_conditions": ["pollen"],
                "recurring_health_patterns": ["throat irritation during poor AQI"],
            }
        }

    async def fake_daily(supabase, user_id, days):
        return {
            "daily_fitness_data": [
                {"log_date": "2026-05-14", "sleep_hours": 5.5, "water_ml": 1000, "hrv_ms": 32},
                {"log_date": "2026-05-13", "sleep_hours": 7.5, "water_ml": 2200, "hrv_ms": 48},
            ],
            "daily_environment_data": [
                {"created_at": "2026-05-14", "aqi": 150, "pollen_level": "High"}
            ],
        }

    monkeypatch.setattr(main, "load_user_health_context", fake_profile)
    monkeypatch.setattr(main, "load_recent_daily_data", fake_daily)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/4/wellness-forecast")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 4
    assert body["headline"]
    assert body["readiness_score"] <= 100
    assert body["environmental_alerts"]
    assert "daily_fitness_data" in body["source_tables"]


def test_wellness_forecast_endpoint_rejects_invalid_user_id(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/0/wellness-forecast")

    assert response.status_code == 422


def test_wellness_forecast_endpoint_handles_storage_unavailable(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    def fail_supabase():
        raise RuntimeError("missing env")

    monkeypatch.setattr(main, "get_supabase", fail_supabase)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/4/wellness-forecast")

    assert response.status_code == 503


def test_daily_log_endpoint_loads_each_daily_table_with_user_and_date_filters(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    supabase = EmptySupabase()
    monkeypatch.setattr(main, "get_supabase", lambda: supabase)

    with TestClient(main.app) as client:
        response = client.get("/api/v1/user/9/daily-log?log_date=2025-10-06")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 9
    assert body["log_date"] == "2025-10-06"

    table_calls = [call for call in supabase.calls if call[0] == "table"]
    assert len(table_calls) == 5
    assert ("table", "daily_fitness_data") in table_calls

    eq_calls = [call for call in supabase.calls if call[0] == "eq"]
    assert eq_calls.count(("eq", "user_id", 9)) == 5
    assert eq_calls.count(("eq", "log_date", "2025-10-06")) == 5


def test_daily_log_endpoint_upserts_all_daily_tables_by_user_and_log_date(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)
    supabase = EmptySupabase()
    monkeypatch.setattr(main, "get_supabase", lambda: supabase)

    payload = {
        "log_date": "2025-10-06",
        "manual": {
            "breakfast_log": "oats",
            "lunch_log": "rice bowl",
            "dinner_log": "dal",
            "snacks_beverages_log": "fruit",
            "mood_today": "Happy",
            "energy_level": "Good",
            "chatbot_symptoms_reported": ["  fatigue  ", ""],
            "workload_intensity": "Moderate",
            "doctor_consulted_today": False,
        },
    }

    with TestClient(main.app) as client:
        response = client.put("/api/v1/user/9/daily-log", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert set(body["saved_tables"]) == {
        "daily_fitness_data",
        "daily_environment_data",
        "daily_device_behavior_data",
        "daily_calendar_data",
        "daily_user_memory_logs",
    }

    upsert_calls = [call for call in supabase.calls if call[0] == "upsert"]
    assert len(upsert_calls) == 5
    assert all(call[1]["user_id"] == 9 for call in upsert_calls)
    assert all(call[1]["log_date"] == "2025-10-06" for call in upsert_calls)
    assert all(call[2] == "user_id,log_date" for call in upsert_calls)

    memory_payload = next(call[1] for call in upsert_calls if "breakfast_log" in call[1])
    assert memory_payload["chatbot_symptoms_reported"] == ["fatigue"]
    assert memory_payload["breakfast"] == "oats"
    assert memory_payload["chatbot_risk_level"] == "Low"

    fitness_payload = next(call[1] for call in upsert_calls if "walking_distance_km" in call[1])
    assert fitness_payload["steps"] > 0
    assert fitness_payload["water_intake_liters"] > 0


def test_daily_log_endpoint_rejects_invalid_enum(monkeypatch):
    monkeypatch.setattr(main, "GrokClient", FakeGrokClient)

    with TestClient(main.app) as client:
        response = client.put(
            "/api/v1/user/9/daily-log",
            json={
                "log_date": "2025-10-06",
                "manual": {"energy_level": "Amazing"},
            },
        )

    assert response.status_code == 422
