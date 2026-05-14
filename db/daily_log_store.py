import asyncio
import logging
from datetime import date
from typing import Any

from supabase import Client

logger = logging.getLogger(__name__)

DAILY_LOG_TIMEOUT_SECONDS = 10.0

DAILY_LOG_TABLES: tuple[str, ...] = (
    "daily_fitness_data",
    "daily_environment_data",
    "daily_device_behavior_data",
    "daily_calendar_data",
    "daily_user_memory_logs",
)


def _normalize_row(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    return {}


def build_automatic_daily_payloads(*, user_id: int, log_date: date) -> dict[str, dict[str, Any]]:
    seed = (log_date.toordinal() + user_id) % 17
    sleep_hours = round(6.4 + ((seed % 5) * 0.35), 2)
    water_liters = round(1.7 + ((seed % 4) * 0.3), 2)
    steps = 4200 + (seed * 310)
    walking_distance = round(steps * 0.00072, 2)
    exercise_minutes = 18 + (seed % 6) * 5
    active_hours = round(2.2 + (seed % 4) * 0.4, 1)
    screen_time = round(4.8 + (seed % 5) * 0.55, 1)
    temperature = 28 + (seed % 7)
    aqi = 62 + (seed * 7)

    return {
        "daily_fitness_data": {
            "steps": steps,
            "sleep_walked": max(0, seed - 4),
            "walking_distance_km": walking_distance,
            "distance_km": walking_distance,
            "calories_burned": 280 + (seed * 18),
            "exercise_duration_minutes": exercise_minutes,
            "exercise_minutes": exercise_minutes,
            "workout_type": "Walking" if seed % 3 else "Mobility",
            "heart_rate_avg": 70 + (seed % 8),
            "resting_heart_rate": 58 + (seed % 7),
            "sedentary_time_hours": round(7.4 - (seed % 4) * 0.25, 1),
            "active_hours": active_hours,
            "sleep_duration_hours": sleep_hours,
            "sleep_hours": sleep_hours,
            "sleep_start_time": "23:20:00",
            "sleep_end_time": "06:35:00",
            "sleep_interruptions": seed % 4,
            "hrv_score": 38 + seed,
            "hrv_ms": 38 + seed,
            "spo2_level": 97 + (seed % 3),
            "spo2_percent": 97 + (seed % 3),
            "body_temperature": round(36.4 + (seed % 4) * 0.08, 2),
            "water_intake_liters": water_liters,
            "water_ml": round(water_liters * 1000),
            "body_weight_kg": round(67.5 + (seed % 3) * 0.2, 1),
            "weight_kg": round(67.5 + (seed % 3) * 0.2, 1),
        },
        "daily_environment_data": {
            "location": "Auto-synced location",
            "temperature_c": temperature,
            "humidity_percent": 54 + (seed % 6) * 4,
            "aqi": aqi,
            "uv_index": 4 + (seed % 6),
            "pollen_level": "High" if seed % 5 == 0 else "Moderate",
            "outdoor_hours": round(0.8 + (seed % 5) * 0.45, 1),
            "heatwave_alert": temperature >= 34,
        },
        "daily_device_behavior_data": {
            "screen_time_hours": screen_time,
            "late_night_usage": seed % 4 == 0,
            "continuous_usage_minutes": 35 + (seed * 4),
            "average_daily_usage_hours": round(screen_time + 0.4, 1),
        },
        "daily_calendar_data": {
            "travel_event": seed % 9 == 0,
            "trip_duration_days": 1 if seed % 9 == 0 else None,
            "meetings_workload": "High" if seed % 4 == 0 else "Moderate",
            "exam_event": seed % 13 == 0,
            "sleep_schedule_disruption": seed % 4 == 0,
        },
    }


async def fetch_daily_log(
    supabase: Client,
    *,
    user_id: int,
    log_date: date,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "user_id": user_id,
        "log_date": log_date.isoformat(),
        "tables": {},
    }

    for table_name in DAILY_LOG_TABLES:
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda table_name=table_name: (
                        supabase.table(table_name)
                        .select("*")
                        .eq("user_id", user_id)
                        .eq("log_date", log_date.isoformat())
                        .maybe_single()
                        .execute()
                    )
                ),
                timeout=DAILY_LOG_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Daily log query timed out", extra={"user_id": user_id, "table": table_name})
            result["tables"][table_name] = {}
            continue
        except Exception:
            logger.error("Daily log query failed", extra={"user_id": user_id, "table": table_name})
            result["tables"][table_name] = {}
            continue

        result["tables"][table_name] = _normalize_row(getattr(response, "data", None))

    return result


async def upsert_daily_log_tables(
    supabase: Client,
    *,
    user_id: int,
    log_date: date,
    table_payloads: dict[str, dict[str, Any]],
) -> list[str]:
    saved_tables: list[str] = []

    for table_name, values in table_payloads.items():
        if table_name not in DAILY_LOG_TABLES:
            continue

        payload = {
            "user_id": user_id,
            "log_date": log_date.isoformat(),
            **values,
        }

        try:
            await asyncio.wait_for(
                asyncio.to_thread(
                    lambda table_name=table_name, payload=payload: (
                        supabase.table(table_name)
                        .upsert(payload, on_conflict="user_id,log_date")
                        .execute()
                    )
                ),
                timeout=DAILY_LOG_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Daily log upsert timed out", extra={"user_id": user_id, "table": table_name})
            raise
        except Exception:
            logger.error("Daily log upsert failed", extra={"user_id": user_id, "table": table_name})
            raise

        saved_tables.append(table_name)

    return saved_tables
