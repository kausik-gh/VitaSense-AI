import asyncio
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from supabase import Client

logger = logging.getLogger(__name__)

SUPABASE_QUERY_TIMEOUT_SECONDS = 10.0

USER_CONTEXT_TABLES: tuple[str, ...] = (
    "user_life_context",
    "user_food_body_relationship",
    "user_medical_identity",
    "user_emotional_wellness",
    "user_personal_context",
    "ai_user_health_profile",
)


@dataclass(frozen=True)
class DailyTableQuery:
    table_name: str
    date_column: str
    order_column: str


DAILY_TABLES: tuple[DailyTableQuery, ...] = (
    DailyTableQuery("daily_fitness_data", "log_date", "log_date"),
    DailyTableQuery("daily_environment_data", "created_at", "created_at"),
    DailyTableQuery("daily_device_behavior_data", "created_at", "created_at"),
    DailyTableQuery("daily_calendar_data", "created_at", "created_at"),
    DailyTableQuery("daily_user_memory_logs", "created_at", "created_at"),
)


def _validate_user_id(user_id: int) -> None:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer")


def _normalize_row(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    return {}


def _normalize_rows(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if isinstance(rows, dict):
        return [rows]
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


async def _execute_with_timeout(query_factory, *, user_id: int, table_name: str):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(lambda: query_factory().execute()),
            timeout=SUPABASE_QUERY_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Supabase query timed out", extra={"user_id": user_id, "table": table_name})
        return None
    except Exception as exc:
        if _is_missing_single_row(exc):
            return None
        logger.error("Supabase query failed", extra={"user_id": user_id, "table": table_name})
        return None


def _is_missing_single_row(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "pgrst116" in message
        or "406" in message
        or "the result contains 0 rows" in message
        or "json object requested" in message
    )


async def _fetch_single_user_row(
    supabase: Client,
    *,
    table_name: str,
    user_id: int,
) -> dict[str, Any]:
    response = await _execute_with_timeout(
        lambda: (
            supabase.table(table_name)
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
        ),
        user_id=user_id,
        table_name=table_name,
    )
    return _normalize_row(getattr(response, "data", None))


async def _fetch_user_rows(
    supabase: Client,
    *,
    query: DailyTableQuery,
    user_id: int,
    cutoff: str,
    limit: int,
) -> list[dict[str, Any]]:
    response = await _execute_with_timeout(
        lambda: (
            supabase.table(query.table_name)
            .select("*")
            .eq("user_id", user_id)
            .gte(query.date_column, cutoff)
            .order(query.order_column, desc=True)
            .limit(limit)
        ),
        user_id=user_id,
        table_name=query.table_name,
    )
    return _normalize_rows(getattr(response, "data", None))


async def load_user_health_context(supabase: Client, user_id: int) -> dict[str, Any]:
    _validate_user_id(user_id)

    context: dict[str, Any] = {"user_id": user_id}
    for table_name in USER_CONTEXT_TABLES:
        context[table_name] = await _fetch_single_user_row(
            supabase,
            table_name=table_name,
            user_id=user_id,
        )
    return context


async def load_recent_daily_data(
    supabase: Client,
    user_id: int,
    days: int = 7,
) -> dict[str, list[dict[str, Any]]]:
    _validate_user_id(user_id)
    if days <= 0:
        raise ValueError("days must be a positive integer")

    cutoff = (date.today() - timedelta(days=days)).isoformat()
    bounded_limit = min(days, 30)

    data: dict[str, list[dict[str, Any]]] = {}
    for query in DAILY_TABLES:
        data[query.table_name] = await _fetch_user_rows(
            supabase,
            query=query,
            user_id=user_id,
            cutoff=cutoff,
            limit=bounded_limit,
        )
    return data
