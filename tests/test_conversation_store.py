import time

import pytest

from grok_client import GrokClient
from state.conversation_store import (
    ConversationState,
    ConversationStore,
    normalize_role,
)


def test_conversation_state_formats_recent_messages_for_grok():
    state = ConversationState(user_id=1, session_id="abc")
    state.add_turn("user", "hello")
    state.add_turn("model", "hi")
    state.add_turn("bot", "checking")

    assert state.to_grok_messages(max_turns=2) == [
        {"role": "assistant", "content": "hi"},
        {"role": "assistant", "content": "checking"},
    ]


def test_role_normalization_is_compatible_with_grok_client(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    state = ConversationState(user_id=1, session_id="abc")
    state.add_turn("ai", "safe response")

    client = GrokClient()

    assert client._normalize_messages(state.to_grok_messages()) == [
        {"role": "assistant", "content": "safe response"}
    ]


def test_invalid_role_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        normalize_role("doctor")


def test_store_isolates_sessions_and_users():
    store = ConversationStore(ttl_seconds=60)

    first = store.get_or_create(1, "same")
    second = store.get_or_create(2, "same")
    third = store.get_or_create(1, "different")

    first.add_turn("user", "first")
    second.add_turn("user", "second")
    third.add_turn("user", "third")

    assert store.get(1, "same") is first
    assert store.get(2, "same") is second
    assert store.get(1, "different") is third
    assert store.size() == 3


def test_expired_session_is_evicted_on_get():
    store = ConversationStore(ttl_seconds=1)
    state = store.get_or_create(1, "expired")
    state.last_active = time.time() - 2

    assert store.get(1, "expired") is None
    assert store.size() == 0


def test_expired_session_is_not_reused_after_recreation():
    store = ConversationStore(ttl_seconds=1)
    expired = store.get_or_create(1, "session")
    expired.add_turn("user", "old")
    expired.last_active = time.time() - 2

    recreated = store.get_or_create(1, "session")

    assert recreated is not expired
    assert recreated.turns == []


def test_evict_expired_removes_only_stale_sessions():
    store = ConversationStore(ttl_seconds=10)
    fresh = store.get_or_create(1, "fresh")
    stale = store.get_or_create(1, "stale")
    stale.last_active = time.time() - 11

    assert store.evict_expired() == 1
    assert store.get(1, "fresh") is fresh
    assert store.get(1, "stale") is None


def test_store_rejects_invalid_keys():
    store = ConversationStore()

    with pytest.raises(ValueError, match="user_id"):
        store.get_or_create(0, "abc")

    with pytest.raises(ValueError, match="session_id"):
        store.get_or_create(1, "")
