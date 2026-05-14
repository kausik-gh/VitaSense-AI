from datetime import date

from wellness.forecast import build_wellness_forecast


def _profile():
    return {
        "user_medical_identity": {
            "allergy_conditions": ["pollen"],
            "recurring_health_patterns": ["throat irritation during poor AQI"],
        },
        "user_life_context": {
            "perceived_health_triggers": ["breathing discomfort in pollution"]
        },
    }


def _daily_data():
    return {
        "daily_fitness_data": [
            {"log_date": "2026-05-14", "sleep_hours": 5.4, "water_ml": 1000, "steps": 2800, "hrv_ms": 35},
            {"log_date": "2026-05-13", "sleep_hours": 7.2, "water_ml": 2200, "steps": 6400, "hrv_ms": 48},
            {"log_date": "2026-05-12", "sleep_hours": 7.0, "water_ml": 2100, "steps": 6100, "hrv_ms": 50},
        ],
        "daily_user_memory_logs": [
            {
                "mood_today": "Stressed",
                "energy_level": "Low",
                "workload_intensity": "High",
                "recovery_status": "Recovering",
            }
        ],
        "daily_environment_data": [
            {
                "created_at": "2026-05-14",
                "aqi": 162,
                "temperature_c": 34,
                "uv_index": 8,
                "pollen_level": "High",
                "outdoor_hours": 2,
            }
        ],
        "daily_device_behavior_data": [
            {"screen_time_hours": 8.5, "late_night_usage": True}
        ],
        "daily_calendar_data": [
            {"meetings_workload": "High", "sleep_schedule_disruption": True}
        ],
    }


def test_forecast_scores_and_narrative_reflect_low_recovery_day():
    forecast = build_wellness_forecast(
        user_id=7,
        user_profile=_profile(),
        daily_data=_daily_data(),
        today=date(2026, 5, 14),
    )

    assert forecast["user_id"] == 7
    assert forecast["date"] == "2026-05-14"
    assert forecast["readiness_score"] < 60
    assert forecast["energy"]["state"] == "delicate"
    assert "Good morning" in forecast["summary"]
    assert forecast["suggested_actions"]
    assert "Front-load hydration" in [action["title"] for action in forecast["suggested_actions"]]


def test_forecast_creates_personalized_environmental_alerts():
    forecast = build_wellness_forecast(
        user_id=7,
        user_profile=_profile(),
        daily_data=_daily_data(),
        today=date(2026, 5, 14),
    )

    alerts = forecast["environmental_alerts"]
    assert {alert["type"] for alert in alerts} >= {"air_quality", "pollen", "heat", "uv"}
    air_alert = next(alert for alert in alerts if alert["type"] == "air_quality")
    assert air_alert["severity"] == "medium"
    assert "throat history" in air_alert["detail"]


def test_forecast_handles_empty_data_gracefully():
    forecast = build_wellness_forecast(
        user_id=1,
        user_profile={},
        daily_data={},
        today=date(2026, 5, 14),
    )

    assert forecast["readiness_score"] >= 0
    assert forecast["patterns"][0]["title"] == "Stable baseline"
    assert forecast["suggested_actions"]
    assert forecast["environmental_alerts"] == []
    assert forecast["source_tables"] == []


def test_forecast_reports_metric_baselines_and_trends():
    forecast = build_wellness_forecast(
        user_id=7,
        user_profile=_profile(),
        daily_data=_daily_data(),
        today=date(2026, 5, 14),
    )

    assert forecast["metrics"]["sleep"]["value"] == 5.4
    assert forecast["metrics"]["sleep"]["baseline"] == 7.1
    assert forecast["metrics"]["sleep"]["trend"] == "below_baseline"
    assert forecast["metrics"]["hydration"]["trend"] == "below_baseline"
