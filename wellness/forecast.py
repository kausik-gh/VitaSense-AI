from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

Severity = Literal["low", "medium", "high"]
Trend = Literal["below_baseline", "near_baseline", "above_baseline", "unknown"]


@dataclass(frozen=True)
class MetricSignal:
    label: str
    value: float | None
    baseline: float | None
    unit: str
    trend: Trend


def _rows(data: dict[str, Any], table_name: str) -> list[dict[str, Any]]:
    value = data.get(table_name)
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def _profile_table(profile: dict[str, Any], table_name: str) -> dict[str, Any]:
    value = profile.get(table_name)
    return value if isinstance(value, dict) else {}


def _number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _first_number(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = _number(row.get(key))
        if value is not None:
            return value
    return None


def _metric(rows: list[dict[str, Any]], keys: str | tuple[str, ...], label: str, unit: str) -> MetricSignal:
    metric_keys = (keys,) if isinstance(keys, str) else keys
    latest = _first_number(rows[0], metric_keys) if rows else None
    baseline_values = [
        value
        for value in (_first_number(row, metric_keys) for row in rows[1:])
        if value is not None
    ]
    baseline = _average(baseline_values)
    trend = _trend(latest, baseline)
    return MetricSignal(label=label, value=latest, baseline=baseline, unit=unit, trend=trend)


def _trend(value: float | None, baseline: float | None, tolerance: float = 0.08) -> Trend:
    if value is None or baseline is None or baseline == 0:
        return "unknown"
    lower = baseline * (1 - tolerance)
    upper = baseline * (1 + tolerance)
    if value < lower:
        return "below_baseline"
    if value > upper:
        return "above_baseline"
    return "near_baseline"


def _severity_from_score(score: int) -> Severity:
    if score < 45:
        return "high"
    if score < 68:
        return "medium"
    return "low"


def _score_label(score: int) -> str:
    if score >= 75:
        return "steady"
    if score >= 55:
        return "watchful"
    return "delicate"


def _bounded_score(score: float) -> int:
    return max(0, min(100, round(score)))


def build_wellness_forecast(
    *,
    user_id: int,
    user_profile: dict[str, Any],
    daily_data: dict[str, Any],
    today: date | None = None,
) -> dict[str, Any]:
    today = today or date.today()

    fitness_rows = _rows(daily_data, "daily_fitness_data")
    memory_rows = _rows(daily_data, "daily_user_memory_logs")
    environment_rows = _rows(daily_data, "daily_environment_data")
    device_rows = _rows(daily_data, "daily_device_behavior_data")
    calendar_rows = _rows(daily_data, "daily_calendar_data")

    metrics = {
        "sleep": _metric(fitness_rows, ("sleep_duration_hours", "sleep_hours"), "Sleep", "h"),
        "hydration": _metric(fitness_rows, ("water_ml", "water_intake_liters"), "Hydration", "ml"),
        "steps": _metric(fitness_rows, "steps", "Activity", "steps"),
        "hrv": _metric(fitness_rows, ("hrv_score", "hrv_ms"), "Recovery", "ms"),
        "screen_time": _metric(device_rows, "screen_time_hours", "Screen time", "h"),
    }

    latest_memory = memory_rows[0] if memory_rows else {}
    latest_environment = environment_rows[0] if environment_rows else {}
    latest_calendar = calendar_rows[0] if calendar_rows else {}
    latest_device = device_rows[0] if device_rows else {}

    energy_score = _energy_score(metrics, latest_memory, latest_calendar, latest_device)
    recovery_score = _recovery_score(metrics, latest_memory, latest_calendar)
    readiness = _bounded_score((energy_score * 0.55) + (recovery_score * 0.45))
    status = _score_label(readiness)

    patterns = _behavior_patterns(metrics, latest_memory, latest_calendar, latest_device)
    actions = _suggested_actions(metrics, latest_memory, latest_environment, latest_calendar)
    environmental_alerts = _environmental_alerts(user_profile, latest_environment)
    narrative = _narrative(status, metrics, patterns, actions, environmental_alerts)

    return {
        "user_id": user_id,
        "date": today.isoformat(),
        "headline": _headline(status, readiness),
        "summary": narrative,
        "readiness_score": readiness,
        "energy": {
            "score": energy_score,
            "state": _score_label(energy_score),
            "trend": _energy_trend(metrics),
        },
        "recovery": {
            "score": recovery_score,
            "state": _score_label(recovery_score),
            "trend": metrics["hrv"].trend,
        },
        "patterns": patterns,
        "suggested_actions": actions,
        "environmental_alerts": environmental_alerts,
        "metrics": {
            key: {
                "label": signal.label,
                "value": signal.value,
                "baseline": signal.baseline,
                "unit": signal.unit,
                "trend": signal.trend,
            }
            for key, signal in metrics.items()
        },
        "source_tables": _source_tables(daily_data, user_profile),
    }


def _energy_score(
    metrics: dict[str, MetricSignal],
    memory: dict[str, Any],
    calendar: dict[str, Any],
    device: dict[str, Any],
) -> int:
    score = 76.0
    sleep = metrics["sleep"].value
    hydration = metrics["hydration"].value
    steps = metrics["steps"].value
    screen_time = metrics["screen_time"].value

    if sleep is not None:
        if sleep < 6:
            score -= 18
        elif sleep < 7:
            score -= 8
        elif sleep >= 8:
            score += 5
    if hydration is not None and hydration < 1500:
        score -= 9
    if steps is not None and steps < 3500:
        score -= 6
    if screen_time is not None and screen_time > 7:
        score -= 7
    if device.get("late_night_usage") is True:
        score -= 6
    if memory.get("energy_level") in {"Very Low", "Low"}:
        score -= 10
    if memory.get("mood_today") in {"Stressed", "Anxious", "Exhausted"}:
        score -= 7
    if memory.get("workload_intensity") in {"High", "Extreme"}:
        score -= 8
    if calendar.get("sleep_schedule_disruption") is True:
        score -= 7

    return _bounded_score(score)


def _recovery_score(
    metrics: dict[str, MetricSignal],
    memory: dict[str, Any],
    calendar: dict[str, Any],
) -> int:
    score = 78.0
    sleep = metrics["sleep"].value
    hrv = metrics["hrv"]

    if sleep is not None and sleep < 6:
        score -= 14
    if hrv.trend == "below_baseline":
        score -= 14
    elif hrv.trend == "above_baseline":
        score += 5
    if memory.get("workload_intensity") in {"High", "Extreme"}:
        score -= 8
    if calendar.get("travel_event") is True:
        score -= 6

    return _bounded_score(score)


def _energy_trend(metrics: dict[str, MetricSignal]) -> Trend:
    if metrics["sleep"].trend == "below_baseline" or metrics["hydration"].trend == "below_baseline":
        return "below_baseline"
    if metrics["sleep"].trend == "above_baseline" and metrics["hrv"].trend != "below_baseline":
        return "above_baseline"
    if metrics["sleep"].trend == "unknown" and metrics["hydration"].trend == "unknown":
        return "unknown"
    return "near_baseline"


def _behavior_patterns(
    metrics: dict[str, MetricSignal],
    memory: dict[str, Any],
    calendar: dict[str, Any],
    device: dict[str, Any],
) -> list[dict[str, str]]:
    patterns: list[dict[str, str]] = []

    if metrics["sleep"].value is not None and metrics["sleep"].value < 6.5:
        patterns.append({
            "title": "Sleep pressure",
            "detail": "Sleep is running light today, which may lower morning energy and stress tolerance.",
        })
    if metrics["hydration"].trend == "below_baseline" or (
        metrics["hydration"].value is not None and metrics["hydration"].value < 1500
    ):
        patterns.append({
            "title": "Hydration drift",
            "detail": "Water intake appears below a supportive range, so fatigue or headache risk may be higher.",
        })
    if memory.get("workload_intensity") in {"High", "Extreme"} or calendar.get("meetings_workload") in {"High", "Extreme"}:
        patterns.append({
            "title": "Workload compression",
            "detail": "Today looks cognitively demanding, so recovery breaks may matter more than usual.",
        })
    if device.get("late_night_usage") is True or (
        metrics["screen_time"].value is not None and metrics["screen_time"].value > 7
    ):
        patterns.append({
            "title": "Screen load",
            "detail": "Recent screen behavior may be adding strain to sleep quality and mental energy.",
        })
    if not patterns:
        patterns.append({
            "title": "Stable baseline",
            "detail": "No strong negative pattern stands out from the available recent data.",
        })

    return patterns[:4]


def _suggested_actions(
    metrics: dict[str, MetricSignal],
    memory: dict[str, Any],
    environment: dict[str, Any],
    calendar: dict[str, Any],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    if metrics["hydration"].value is None or metrics["hydration"].value < 1800:
        actions.append({
            "title": "Front-load hydration",
            "detail": "Add water earlier in the day rather than waiting until evening.",
        })
    if metrics["sleep"].value is not None and metrics["sleep"].value < 6.5:
        actions.append({
            "title": "Keep the afternoon lighter",
            "detail": "A lighter afternoon workload may help protect energy if your schedule allows it.",
        })
    if environment.get("aqi") and _number(environment.get("aqi")) and _number(environment.get("aqi")) >= 120:
        actions.append({
            "title": "Reduce outdoor exposure",
            "detail": "Poor air quality may make indoor or low-exertion plans more supportive today.",
        })
    if memory.get("mood_today") in {"Stressed", "Anxious"} or calendar.get("meetings_workload") in {"High", "Extreme"}:
        actions.append({
            "title": "Create one decompression window",
            "detail": "A short quiet reset between high-focus blocks may reduce stress carryover.",
        })
    if not actions:
        actions.append({
            "title": "Maintain your rhythm",
            "detail": "Keep meals, movement, and wind-down timing steady today.",
        })

    return actions[:3]


def _environmental_alerts(
    user_profile: dict[str, Any],
    environment: dict[str, Any],
) -> list[dict[str, str]]:
    medical = _profile_table(user_profile, "user_medical_identity")
    life = _profile_table(user_profile, "user_life_context")
    allergies = " ".join(str(item).lower() for item in medical.get("allergy_conditions", []) or [])
    recurring = " ".join(str(item).lower() for item in medical.get("recurring_health_patterns", []) or [])
    triggers = " ".join(str(item).lower() for item in life.get("perceived_health_triggers", []) or [])

    alerts: list[dict[str, str]] = []
    aqi = _number(environment.get("aqi"))
    uv_index = _number(environment.get("uv_index"))
    pollen = str(environment.get("pollen_level", "")).lower()
    temperature = _number(environment.get("temperature_c"))
    outdoor_hours = _number(environment.get("outdoor_hours"))

    if aqi is not None and aqi >= 120:
        severity: Severity = "high" if aqi >= 180 else "medium"
        detail = "Air quality is elevated today."
        if "throat" in recurring or "asthma" in allergies or "breathing" in triggers:
            detail = "Air quality is elevated and may be more relevant because of your respiratory or throat history."
        alerts.append({
            "type": "air_quality",
            "severity": severity,
            "title": "AQI sensitivity watch",
            "detail": detail,
        })

    if pollen in {"high", "very high"} or (pollen and "allerg" in allergies):
        alerts.append({
            "type": "pollen",
            "severity": "medium",
            "title": "Allergy load",
            "detail": "Pollen may be more noticeable today based on your allergy context.",
        })

    if temperature is not None and temperature >= 33 and outdoor_hours is not None and outdoor_hours >= 1:
        alerts.append({
            "type": "heat",
            "severity": "medium",
            "title": "Heat exposure",
            "detail": "Heat plus outdoor time may increase fatigue and hydration needs today.",
        })

    if uv_index is not None and uv_index >= 7:
        alerts.append({
            "type": "uv",
            "severity": "low",
            "title": "UV intensity",
            "detail": "UV is high enough that shade and skin protection may be helpful outdoors.",
        })

    return alerts[:4]


def _headline(status: str, readiness: int) -> str:
    if status == "steady":
        return f"Today looks steady with {readiness}% readiness."
    if status == "watchful":
        return f"Today may need a gentler rhythm with {readiness}% readiness."
    return f"Today may feel more delicate with {readiness}% readiness."


def _narrative(
    status: str,
    metrics: dict[str, MetricSignal],
    patterns: list[dict[str, str]],
    actions: list[dict[str, str]],
    environmental_alerts: list[dict[str, str]],
) -> str:
    opening = {
        "steady": "Good morning. Your recent signals look relatively steady today.",
        "watchful": "Good morning. Your signals suggest today may be a watchful day.",
        "delicate": "Good morning. Your body may benefit from a more supportive pace today.",
    }[status]

    context = []
    if metrics["sleep"].value is not None:
        context.append(f"sleep is at {metrics['sleep'].value:g}h")
    if metrics["hydration"].value is not None:
        context.append(f"hydration is around {metrics['hydration'].value:g}ml")
    if patterns:
        context.append(patterns[0]["title"].lower())
    if environmental_alerts:
        context.append(environmental_alerts[0]["title"].lower())

    context_sentence = ""
    if context:
        context_sentence = " Based on " + ", ".join(context[:3]) + ", your energy may shift through the day."

    action_sentence = ""
    if actions:
        action_sentence = f" {actions[0]['detail']}"

    return opening + context_sentence + action_sentence


def _source_tables(daily_data: dict[str, Any], user_profile: dict[str, Any]) -> list[str]:
    sources = [
        table
        for table, rows in daily_data.items()
        if isinstance(rows, list) and rows
    ]
    sources.extend(
        table
        for table, row in user_profile.items()
        if isinstance(row, dict) and row
    )
    return sorted(set(sources))
