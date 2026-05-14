from types import SimpleNamespace

import pytest

import chat.orchestrator as orchestrator
from chat.safety_scanner import DISCLAIMER, ESCALATION_MESSAGE
from state.conversation_store import ConversationStore


class FakeStream:
    def __init__(self, chunks):
        self.chunks = chunks

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self.chunks):
            raise StopAsyncIteration
        value = self.chunks[self._index]
        self._index += 1
        return SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content=value))]
        )


class FakeGrokClient:
    def __init__(self, chunks=None, error=False):
        self.chunks = chunks or []
        self.error = error
        self.calls = []

    async def chat(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        if self.error:
            raise RuntimeError("stream failed")
        return FakeStream(self.chunks)


class FakeInsert:
    def __init__(self, table_name, payload, inserts):
        self.table_name = table_name
        self.payload = payload
        self.inserts = inserts

    def execute(self):
        self.inserts.append((self.table_name, self.payload))
        return SimpleNamespace(data=[self.payload])


class FakeTable:
    def __init__(self, table_name, inserts):
        self.table_name = table_name
        self.inserts = inserts

    def insert(self, payload):
        return FakeInsert(self.table_name, payload, self.inserts)


class FakeSupabase:
    def __init__(self):
        self.inserts = []

    def table(self, table_name):
        return FakeTable(table_name, self.inserts)


class FailingInsert:
    def execute(self):
        raise RuntimeError("insert failed")


class FailingTable:
    def insert(self, payload):
        return FailingInsert()


class FailingSupabase:
    def table(self, table_name):
        return FailingTable()


async def _collect_async(generator):
    return [item async for item in generator]


def _join_sse_data(events):
    payload = []
    for event in events:
        for line in event.splitlines():
            if line.startswith("data: "):
                value = line.removeprefix("data: ")
                if value != "[DONE]":
                    payload.append(value)
    return "".join(payload)


def _deps(grok, supabase, store=None):
    return orchestrator.OrchestratorDependencies(
        grok_client=grok,
        supabase_factory=lambda: supabase,
        store=store or ConversationStore(ttl_seconds=60),
    )


async def _empty_profile(supabase, user_id):
    return {}


async def _empty_daily(supabase, user_id, days):
    return {}


def test_chunk_text_preserves_words():
    assert orchestrator._chunk_text("alpha beta gamma", chunk_size=10) == [
        "alpha beta ",
        "gamma",
    ]
    assert "".join(orchestrator._chunk_text("alpha beta gamma", chunk_size=10)) == "alpha beta gamma"


@pytest.mark.asyncio
async def test_stream_chat_sse_always_emits_done(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    deps = _deps(FakeGrokClient(chunks=["One possible explanation."]), FakeSupabase())

    events = await _collect_async(
        orchestrator.stream_chat_sse(1, "session", "I feel tired", dependencies=deps)
    )

    assert events[-1] == "data: [DONE]\n\n"
    assert any("One possible explanation" in event for event in events)


@pytest.mark.asyncio
async def test_emergency_precheck_blocks_before_grok(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    grok = FakeGrokClient(chunks=["should not be called"])
    supabase = FakeSupabase()
    store = ConversationStore(ttl_seconds=60)

    events = await _collect_async(
        orchestrator.stream_chat_sse(
            1,
            "session",
            "I have chest pain",
            dependencies=_deps(grok, supabase, store),
        )
    )

    assert grok.calls == []
    assert ESCALATION_MESSAGE in "".join(events)
    assert events[-1] == "data: [DONE]\n\n"
    assert store.get(1, "session").escalation_flag is True
    assert supabase.inserts[-1][1]["ai_risk_level"] == "Critical"


@pytest.mark.asyncio
async def test_context_is_injected_into_grok_system_prompt(monkeypatch):
    async def fake_profile(supabase, user_id):
        return {
            "user_life_context": {"life_phase": "Early Career"},
            "user_medical_identity": {"allergy_conditions": ["pollen"]},
        }

    async def fake_daily(supabase, user_id, days):
        return {
            "daily_fitness_data": [
                {"log_date": "2026-05-14", "sleep_hours": 5.5, "steps": 3000}
            ],
            "daily_environment_data": [{"created_at": "2026-05-14", "aqi": 140}],
        }

    monkeypatch.setattr(orchestrator, "load_user_health_context", fake_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", fake_daily)
    grok = FakeGrokClient(chunks=["This may be related to sleep. " + DISCLAIMER])

    await _collect_async(
        orchestrator.handle_chat_message(
            1,
            "session",
            "Why am I tired?",
            dependencies=_deps(grok, FakeSupabase()),
        )
    )

    system_prompt = grok.calls[0]["messages"][0]["content"]
    assert "Life phase: Early Career" in system_prompt
    assert "Allergies: pollen" in system_prompt
    assert "Sleep 5.5h" in system_prompt
    assert "AQI 140" in system_prompt


@pytest.mark.asyncio
async def test_postcheck_appends_disclaimer_before_streaming(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    deps = _deps(FakeGrokClient(chunks=["One possible explanation is dehydration."]), FakeSupabase())

    chunks = await _collect_async(
        orchestrator.handle_chat_message(1, "session", "I feel tired", dependencies=deps)
    )

    response = "".join(chunks)
    assert "One possible explanation is dehydration." in response
    assert DISCLAIMER in response


@pytest.mark.asyncio
async def test_ai_emergency_output_is_replaced_before_streaming(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    deps = _deps(FakeGrokClient(chunks=["The user reports chest pain."]), FakeSupabase())

    chunks = await _collect_async(
        orchestrator.handle_chat_message(1, "session", "I feel odd", dependencies=deps)
    )

    assert "".join(chunks) == ESCALATION_MESSAGE


@pytest.mark.asyncio
async def test_grok_stream_failure_recovers_and_sse_completes(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    deps = _deps(FakeGrokClient(error=True), FakeSupabase())

    events = await _collect_async(
        orchestrator.stream_chat_sse(1, "session", "I feel tired", dependencies=deps)
    )

    joined = _join_sse_data(events)
    assert orchestrator.STREAM_ERROR_MESSAGE in joined
    assert DISCLAIMER in joined
    assert events[-1] == "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_sse_emits_done_when_orchestration_raises(monkeypatch):
    async def broken_handle_chat_message(*args, **kwargs):
        if False:
            yield ""
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(orchestrator, "handle_chat_message", broken_handle_chat_message)

    events = await _collect_async(
        orchestrator.stream_chat_sse(
            1,
            "session",
            "I feel tired",
            dependencies=_deps(FakeGrokClient(), FakeSupabase()),
        )
    )

    assert orchestrator.STREAM_ERROR_MESSAGE in "".join(events)
    assert events[-1] == "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_persist_turn_failure_does_not_raise():
    await orchestrator.persist_turn(
        FailingSupabase(),
        user_id=5,
        session_id="abc",
        role="assistant",
        content="This could suggest fatigue.",
    )


@pytest.mark.asyncio
async def test_persistence_hooks_store_user_and_assistant_turns(monkeypatch):
    monkeypatch.setattr(orchestrator, "load_user_health_context", _empty_profile)
    monkeypatch.setattr(orchestrator, "load_recent_daily_data", _empty_daily)
    supabase = FakeSupabase()
    deps = _deps(FakeGrokClient(chunks=["This could suggest fatigue. " + DISCLAIMER]), supabase)

    await _collect_async(
        orchestrator.handle_chat_message(3, "abc", "I feel tired", dependencies=deps)
    )

    assert [item[0] for item in supabase.inserts] == [
        "chatbot_conversation_history",
        "chatbot_conversation_history",
    ]
    assert supabase.inserts[0][1]["message_role"] == "user"
    assert supabase.inserts[0][1]["user_id"] == 3
    assert supabase.inserts[0][1]["session_id"] == "abc"
    assert supabase.inserts[1][1]["message_role"] == "assistant"
