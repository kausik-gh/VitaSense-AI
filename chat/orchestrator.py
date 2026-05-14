from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable

from chat.prompt_builder import build_system_prompt
from chat.safety_scanner import (
    ESCALATION_MESSAGE,
    SafetyResult,
    scan_ai_response,
    scan_user_message,
)
from db.supabase_client import get_supabase
from db.user_context_loader import load_recent_daily_data, load_user_health_context
from grok_client import GrokClient
from state.conversation_store import ConversationStore, conversation_store

logger = logging.getLogger(__name__)

STREAM_ERROR_MESSAGE = (
    "I could not complete the response right now. Please try again in a moment."
)
PERSIST_TIMEOUT_SECONDS = 10.0
STREAM_CHUNK_SIZE = 80


@dataclass(frozen=True)
class OrchestratorDependencies:
    grok_client: GrokClient
    supabase_factory: Callable[[], Any] = get_supabase
    store: ConversationStore = conversation_store


def format_sse_event(data: str) -> str:
    lines = data.splitlines()
    if not lines:
        lines = [""]
    return "".join(f"data: {line}\n" for line in lines) + "\n"


async def persist_turn(
    supabase: Any,
    *,
    user_id: int,
    session_id: str,
    role: str,
    content: str,
    symptoms: list[str] | None = None,
    risk_level: str | None = None,
) -> None:
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message_role": role,
        "message_content": content,
        "related_symptoms": symptoms or [],
        "ai_risk_level": risk_level,
    }

    try:
        await asyncio.wait_for(
            asyncio.to_thread(
                lambda: supabase.table("chatbot_conversation_history").insert(payload).execute()
            ),
            timeout=PERSIST_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error(
            "Conversation persistence timed out",
            extra={"user_id": user_id, "session_id": session_id},
        )
    except Exception:
        logger.error(
            "Conversation persistence failed",
            extra={"user_id": user_id, "session_id": session_id},
        )


def _extract_delta(chunk: Any) -> str:
    try:
        return chunk.choices[0].delta.content or ""
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""


async def _collect_grok_response(
    grok_client: GrokClient,
    messages: list[dict[str, str]],
) -> str:
    stream = await grok_client.chat(
        messages,
        stream=True,
        temperature=0.3,
        max_tokens=600,
    )

    parts: list[str] = []
    async for chunk in stream:
        delta = _extract_delta(chunk)
        if delta:
            parts.append(delta)
    return "".join(parts)


def _chunk_text(text: str, chunk_size: int = STREAM_CHUNK_SIZE) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    remaining = text
    while len(remaining) > chunk_size:
        split_at = remaining.rfind(" ", 0, chunk_size + 1)
        if split_at <= 0:
            split_at = chunk_size
        else:
            split_at += 1
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]

    if remaining:
        chunks.append(remaining)
    return chunks


async def handle_chat_message(
    user_id: int,
    session_id: str,
    user_message: str,
    *,
    dependencies: OrchestratorDependencies,
) -> AsyncGenerator[str, None]:
    supabase = None
    user_scan = scan_user_message(user_message)

    try:
        supabase = dependencies.supabase_factory()
    except Exception:
        logger.error(
            "Supabase client unavailable for chat orchestration",
            extra={"user_id": user_id, "session_id": session_id},
        )

    if user_scan.verdict == SafetyResult.BLOCK:
        response_text = user_scan.modified_response or ESCALATION_MESSAGE
        state = dependencies.store.get_or_create(user_id, session_id)
        state.escalation_flag = True
        state.add_turn("user", user_message)
        state.add_turn("assistant", response_text)

        if supabase is not None:
            await persist_turn(supabase, user_id=user_id, session_id=session_id, role="user", content=user_message)
            await persist_turn(
                supabase,
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=response_text,
                risk_level="Critical",
            )

        yield response_text
        return

    state = dependencies.store.get_or_create(user_id, session_id)
    state.add_turn("user", user_message)

    user_profile: dict[str, Any] = {}
    daily_data: dict[str, Any] = {}
    if supabase is not None:
        try:
            user_profile, daily_data = await asyncio.gather(
                load_user_health_context(supabase, user_id),
                load_recent_daily_data(supabase, user_id, 7),
            )
        except Exception:
            logger.error(
                "Context injection failed",
                extra={"user_id": user_id, "session_id": session_id},
            )

    system_prompt = build_system_prompt(
        user_profile=user_profile,
        daily_data=daily_data,
        hypotheses=state.hypotheses,
        follow_up_queue=state.follow_up_queue,
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(state.to_grok_messages(max_turns=10))

    try:
        raw_response = await _collect_grok_response(dependencies.grok_client, messages)
    except Exception:
        logger.error(
            "Grok streaming failed",
            extra={"user_id": user_id, "session_id": session_id},
        )
        raw_response = STREAM_ERROR_MESSAGE

    ai_scan = scan_ai_response(raw_response)
    if ai_scan.verdict == SafetyResult.BLOCK:
        response_text = ai_scan.modified_response or ESCALATION_MESSAGE
        state.escalation_flag = True
        risk_level = "Critical"
    elif ai_scan.verdict == SafetyResult.FLAG and ai_scan.modified_response:
        response_text = ai_scan.modified_response
        risk_level = None
    else:
        response_text = ai_scan.modified_response or raw_response
        risk_level = None

    state.add_turn("assistant", response_text)

    if supabase is not None:
        await persist_turn(supabase, user_id=user_id, session_id=session_id, role="user", content=user_message)
        await persist_turn(
            supabase,
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=response_text,
            risk_level=risk_level,
        )

    for chunk in _chunk_text(response_text):
        yield chunk


async def stream_chat_sse(
    user_id: int,
    session_id: str,
    user_message: str,
    *,
    dependencies: OrchestratorDependencies,
) -> AsyncGenerator[str, None]:
    try:
        async for token in handle_chat_message(
            user_id,
            session_id,
            user_message,
            dependencies=dependencies,
        ):
            yield format_sse_event(token)
    except Exception:
        logger.error(
            "SSE chat stream failed",
            extra={"user_id": user_id, "session_id": session_id},
        )
        yield format_sse_event(STREAM_ERROR_MESSAGE)
    finally:
        yield format_sse_event("[DONE]")
