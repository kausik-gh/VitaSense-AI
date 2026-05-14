import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

ROLE_MAP = {"model": "assistant", "bot": "assistant", "ai": "assistant"}
ALLOWED_ROLES = {"system", "user", "assistant", "tool"}


def normalize_role(role: str) -> str:
    normalized = ROLE_MAP.get(role.lower(), role.lower())
    if normalized not in ALLOWED_ROLES:
        raise ValueError("Unsupported conversation role")
    return normalized


@dataclass
class ConversationState:
    user_id: int
    session_id: str
    turns: list[dict[str, Any]] = field(default_factory=list)
    active_symptoms: list[str] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    follow_up_queue: list[str] = field(default_factory=list)
    escalation_flag: bool = False
    last_active: float = field(default_factory=time.time)

    def add_turn(self, role: str, content: str) -> None:
        normalized_role = normalize_role(role)
        self.turns.append(
            {
                "role": normalized_role,
                "content": str(content),
                "ts": time.time(),
            }
        )
        self.last_active = time.time()

    def to_grok_messages(self, max_turns: int = 10) -> list[dict[str, str]]:
        if max_turns <= 0:
            return []

        recent_turns = self.turns[-max_turns:]
        return [
            {
                "role": normalize_role(str(turn["role"])),
                "content": str(turn["content"]),
            }
            for turn in recent_turns
        ]


class ConversationStore:
    TTL_SECONDS = 4 * 3600

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl_seconds = ttl_seconds or self.TTL_SECONDS
        self._store: dict[str, ConversationState] = {}
        self._lock = threading.RLock()

    def _key(self, user_id: int, session_id: str) -> str:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        if not session_id:
            raise ValueError("session_id must be provided")
        return f"{user_id}:{session_id}"

    def _is_expired(self, state: ConversationState) -> bool:
        return (time.time() - state.last_active) > self.ttl_seconds

    def get(self, user_id: int, session_id: str) -> ConversationState | None:
        key = self._key(user_id, session_id)
        with self._lock:
            state = self._store.get(key)
            if state is None:
                return None
            if self._is_expired(state):
                del self._store[key]
                logger.info("Expired conversation state evicted", extra={"user_id": user_id, "session_id": session_id})
                return None
            return state

    def get_or_create(self, user_id: int, session_id: str) -> ConversationState:
        key = self._key(user_id, session_id)
        with self._lock:
            state = self.get(user_id, session_id)
            if state is not None:
                return state

            state = ConversationState(user_id=user_id, session_id=session_id)
            self._store[key] = state
            return state

    def evict_expired(self) -> int:
        with self._lock:
            expired_keys = [
                key for key, state in self._store.items() if self._is_expired(state)
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._store)


conversation_store = ConversationStore()
