from chat.prompt_builder import (
    DISCLAIMER,
    ESCALATION_MESSAGE,
    MAX_PROMPT_TOKENS,
    PromptBuilder,
    build_system_prompt,
    estimate_tokens,
)


def _sample_profile():
    return {
        "user_life_context": {
            "life_phase": "Early Career",
            "lifestyle_identity": "Highly Busy",
            "preferred_environment": "Indoor Controlled Environment",
            "perceived_health_triggers": ["poor sleep", "poor sleep", "high workload"],
        },
        "user_food_body_relationship": {
            "eating_behavior": "Irregular Eating",
            "body_awareness_level": "Aware",
        },
        "user_medical_identity": {
            "chronic_conditions": ["asthma"],
            "allergy_conditions": ["pollen"],
            "recurring_health_patterns": ["throat irritation during poor AQI"],
        },
        "user_emotional_wellness": {
            "stress_response_pattern": "Sleep",
            "recovery_preference": "Rest",
        },
        "user_personal_context": {
            "personal_context_summary": "Usually works late during release weeks.",
        },
        "ai_user_health_profile": {
            "ai_health_summary": "Sleep dips and workload spikes often precede low energy.",
            "ai_risk_factors": ["low hydration", "late night screen time"],
        },
    }


def _sample_daily_data():
    return {
        "daily_fitness_data": [
            {
                "log_date": "2026-05-14",
                "heart_rate_avg": 78,
                "hrv_ms": 42,
                "spo2_percent": 98,
                "sleep_hours": 5.5,
                "sleep_quality_score": 62,
                "steps": 4200,
                "exercise_minutes": 12,
                "water_ml": 1100,
            }
        ],
        "daily_user_memory_logs": [
            {
                "breakfast": "toast",
                "lunch": "rice bowl",
                "dinner": "late noodles",
                "snacks": "chips",
                "symptom_today": ["fatigue"],
                "chatbot_symptoms": ["fatigue"],
                "mood_today": "Stressed",
                "energy_level": "Low",
                "workload_intensity": "High",
                "recovery_status": "Recovering",
            }
        ],
        "daily_environment_data": [
            {
                "created_at": "2026-05-14",
                "aqi": 142,
                "temperature_c": 34,
                "humidity_percent": 70,
                "uv_index": 8,
                "pollen_level": "High",
                "outdoor_hours": 2,
            }
        ],
        "daily_device_behavior_data": [
            {
                "screen_time_hours": 8,
                "late_night_usage": True,
                "continuous_usage_minutes": 95,
            }
        ],
        "daily_calendar_data": [
            {
                "travel_event": False,
                "exam_event": False,
                "meetings_workload": "High",
                "sleep_schedule_disruption": True,
            }
        ],
    }


def test_build_system_prompt_contains_required_safety_and_uncertainty_rules():
    prompt = build_system_prompt(_sample_profile(), _sample_daily_data(), [], [])

    assert "may be related to" in prompt
    assert "one possible explanation" in prompt
    assert "this could suggest" in prompt
    assert "Never say \"You have X\"" in prompt
    assert "Ask at most ONE follow-up question" in prompt
    assert ESCALATION_MESSAGE in prompt
    assert DISCLAIMER in prompt
    assert "chest pain" in prompt
    assert "heart attack" in prompt


def test_profile_and_daily_context_blocks_are_formatted():
    prompt = build_system_prompt(_sample_profile(), _sample_daily_data(), [], [])

    assert "# USER HEALTH PROFILE" in prompt
    assert "Life phase: Early Career" in prompt
    assert "Allergies: pollen" in prompt
    assert "# RECENT HEALTH CONTEXT (last 7 days)" in prompt
    assert "Latest vitals (2026-05-14)" in prompt
    assert "Recent meals: breakfast: toast; lunch: rice bowl; dinner: late noodles; snacks: chips" in prompt
    assert "Environment (2026-05-14)" in prompt


def test_hypotheses_are_sorted_limited_and_hedged():
    prompt = build_system_prompt(
        _sample_profile(),
        _sample_daily_data(),
        [
            {"cause": "low hydration", "probability": 0.4, "confidence": "medium"},
            {"cause": "poor sleep", "probability": 0.8, "confidence": "high", "evidence": ["5.5h sleep"]},
            {"cause": "screen fatigue", "probability": 0.5},
            {"cause": "extra item", "probability": 0.9},
        ],
        [],
    )

    hypothesis_block = prompt.split("# ACTIVE HYPOTHESES", 1)[1]

    assert "# ACTIVE HYPOTHESES" in prompt
    assert hypothesis_block.index("extra item") < hypothesis_block.index("poor sleep") < hypothesis_block.index("screen fatigue")
    assert "low hydration" not in hypothesis_block
    assert "probability: 80%" in prompt
    assert "evidence: 5.5h sleep" in prompt


def test_follow_up_queue_uses_only_first_question():
    prompt = build_system_prompt(
        _sample_profile(),
        _sample_daily_data(),
        [],
        ["How severe is it from 1-10?", "Do you have fever?"],
    )

    assert "Ask this question next (and only this one): How severe is it from 1-10?" in prompt
    assert "Do you have fever?" not in prompt


def test_default_follow_up_strategy_is_present_when_queue_empty():
    prompt = build_system_prompt(_sample_profile(), _sample_daily_data(), [], [])

    assert "If clarification is needed, ask exactly ONE" in prompt


def test_prompt_stays_within_token_budget_for_large_context():
    large_profile = _sample_profile()
    large_profile["ai_user_health_profile"]["ai_health_summary"] = " ".join(["summary"] * 2000)
    large_daily = _sample_daily_data()
    large_daily["daily_user_memory_logs"][0]["personal_daily_note"] = " ".join(["note"] * 2000)

    prompt = build_system_prompt(
        large_profile,
        large_daily,
        [{"cause": "stress", "probability": 0.7, "evidence": [" ".join(["evidence"] * 500)]}],
        [" ".join(["question"] * 500)],
    )

    assert estimate_tokens(prompt) <= MAX_PROMPT_TOKENS
    assert ESCALATION_MESSAGE in prompt
    assert DISCLAIMER in prompt


def test_duplicate_context_lines_are_suppressed():
    profile = {
        "user_life_context": {"life_phase": "Early Career"},
        "ai_user_health_profile": {},
    }

    prompt = build_system_prompt(profile, {}, [], [])

    assert prompt.count("Life phase: Early Career") == 1


def test_prompt_builder_can_use_smaller_budget():
    prompt = PromptBuilder(max_prompt_tokens=260).build(
        user_profile=_sample_profile(),
        daily_data=_sample_daily_data(),
        hypotheses=[],
        follow_up_queue=[],
    )

    assert estimate_tokens(prompt) <= 260
    assert ESCALATION_MESSAGE in prompt
