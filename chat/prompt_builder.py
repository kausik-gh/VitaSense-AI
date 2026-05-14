from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chat.safety_scanner import DISCLAIMER, ESCALATION_MESSAGE

MAX_PROMPT_TOKENS = 1200
MAX_PROFILE_TOKENS = 220
MAX_DAILY_TOKENS = 330
MAX_HYPOTHESIS_TOKENS = 120
MAX_FOLLOW_UP_TOKENS = 80

ROLE_BLOCK = f"""You are a personalized AI health assistant with access to this user's complete health history. You are NOT a doctor and must never present yourself as one.

CORE RULES:
- Use only probabilistic language: "may be related to", "one possible explanation", "this could suggest", "based on your history it's possible that"
- Never say "You have X" or "This is definitely Y"
- Ask at most ONE follow-up question per turn
- If the user reports any emergency symptom listed below, output the escalation message immediately and nothing else
- End every health response with the disclaimer

EMERGENCY ESCALATION TRIGGERS - if ANY of these appear, output ONLY the escalation message:
chest pain, difficulty breathing, shortness of breath, blood in vomit, blood in stool, blood in urine, sudden severe headache, loss of consciousness, fainting, facial drooping, arm weakness, speech difficulty, throat swelling, anaphylaxis, overdose, poisoning, stroke, heart attack

ESCALATION MESSAGE:
{ESCALATION_MESSAGE}

DISCLAIMER (append to every health response):
{DISCLAIMER}"""

DEFAULT_FOLLOW_UP = (
    "If clarification is needed, ask exactly ONE of: symptom duration, severity (1-10), "
    "fever/chills present, what was eaten in last 24h, whether this has happened before."
)


def estimate_tokens(text: str) -> int:
    return len(text.split())


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _join_list(value: Any) -> str:
    items = [str(item) for item in _as_list(value) if item not in (None, "")]
    return ", ".join(items)


def _truncate_words(text: str, max_tokens: int) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens]).rstrip(" ,;:") + "..."


def _append_unique(lines: list[str], seen: set[str], line: str | None) -> None:
    if not line:
        return
    normalized = " ".join(line.split()).lower()
    if normalized in seen:
        return
    seen.add(normalized)
    lines.append(line)


@dataclass(frozen=True)
class PromptBuilder:
    max_prompt_tokens: int = MAX_PROMPT_TOKENS
    max_profile_tokens: int = MAX_PROFILE_TOKENS
    max_daily_tokens: int = MAX_DAILY_TOKENS
    max_hypothesis_tokens: int = MAX_HYPOTHESIS_TOKENS
    max_follow_up_tokens: int = MAX_FOLLOW_UP_TOKENS

    def build(
        self,
        *,
        user_profile: dict[str, Any],
        daily_data: dict[str, Any],
        hypotheses: list[dict[str, Any]],
        follow_up_queue: list[str],
    ) -> str:
        blocks = [ROLE_BLOCK]

        profile_block = self._build_profile_block(user_profile)
        if profile_block:
            blocks.append(profile_block)

        daily_block = self._build_daily_block(daily_data)
        if daily_block:
            blocks.append(daily_block)

        hypothesis_block = self._build_hypothesis_block(hypotheses)
        if hypothesis_block:
            blocks.append(hypothesis_block)

        blocks.append(self._build_follow_up_block(follow_up_queue))

        return self._fit_prompt(blocks)

    def _build_profile_block(self, user_profile: dict[str, Any]) -> str:
        lines: list[str] = []
        seen: set[str] = set()

        life = user_profile.get("user_life_context", {}) or {}
        food = user_profile.get("user_food_body_relationship", {}) or {}
        medical = user_profile.get("user_medical_identity", {}) or {}
        emotional = user_profile.get("user_emotional_wellness", {}) or {}
        personal = user_profile.get("user_personal_context", {}) or {}
        ai_profile = user_profile.get("ai_user_health_profile", {}) or {}

        _append_unique(lines, seen, self._field("Life phase", life.get("life_phase")))
        _append_unique(lines, seen, self._field("Social environment", life.get("social_environment")))
        _append_unique(lines, seen, self._field("Lifestyle", life.get("lifestyle_identity")))
        _append_unique(lines, seen, self._field("Preferred environment", life.get("preferred_environment")))
        _append_unique(lines, seen, self._field("Health triggers", _join_list(life.get("perceived_health_triggers"))))
        _append_unique(lines, seen, self._field("Eating behavior", food.get("eating_behavior")))
        _append_unique(lines, seen, self._field("Body awareness", food.get("body_awareness_level")))
        _append_unique(lines, seen, self._field("Chronic conditions", _join_list(medical.get("chronic_conditions"))))
        _append_unique(lines, seen, self._field("Allergies", _join_list(medical.get("allergy_conditions"))))
        _append_unique(lines, seen, self._field("Recurring patterns", _join_list(medical.get("recurring_health_patterns"))))
        _append_unique(lines, seen, self._field("Stress response", emotional.get("stress_response_pattern")))
        _append_unique(lines, seen, self._field("Recovery preference", emotional.get("recovery_preference")))
        _append_unique(lines, seen, self._field("Personal context", personal.get("personal_context_summary")))
        _append_unique(lines, seen, self._field("AI health summary", ai_profile.get("ai_health_summary")))
        _append_unique(lines, seen, self._field("Known risk factors", _join_list(ai_profile.get("ai_risk_factors"))))

        if not lines:
            return ""

        body = _truncate_words("\n".join(lines), self.max_profile_tokens)
        return "# USER HEALTH PROFILE\n" + body

    def _build_daily_block(self, daily_data: dict[str, Any]) -> str:
        lines: list[str] = []
        seen: set[str] = set()

        fitness_rows = _as_list(daily_data.get("daily_fitness_data"))
        if fitness_rows and isinstance(fitness_rows[0], dict):
            latest = fitness_rows[0]
            _append_unique(
                lines,
                seen,
                "Latest vitals "
                f"({latest.get('log_date', latest.get('created_at', 'recent'))}): "
                f"HR avg {latest.get('heart_rate_avg', 'N/A')} bpm, "
                f"HRV {latest.get('hrv_ms', 'N/A')} ms, "
                f"SpO2 {latest.get('spo2_percent', 'N/A')}%, "
                f"Sleep {latest.get('sleep_hours', 'N/A')}h, "
                f"Sleep quality {latest.get('sleep_quality_score', 'N/A')}, "
                f"Steps {latest.get('steps', 'N/A')}, "
                f"Exercise {latest.get('exercise_minutes', 'N/A')} min, "
                f"Water {latest.get('water_ml', 'N/A')} ml.",
            )

        memory_rows = _as_list(daily_data.get("daily_user_memory_logs"))
        if memory_rows and isinstance(memory_rows[0], dict):
            latest_memory = memory_rows[0]
            meals = [
                f"{meal}: {latest_memory[meal]}"
                for meal in ("breakfast", "lunch", "dinner", "snacks")
                if latest_memory.get(meal)
            ]
            _append_unique(lines, seen, self._field("Recent meals", "; ".join(meals)))
            _append_unique(lines, seen, self._field("Symptoms today", _join_list(latest_memory.get("symptom_today"))))
            _append_unique(lines, seen, self._field("Chatbot symptoms", _join_list(latest_memory.get("chatbot_symptoms"))))
            _append_unique(lines, seen, self._field("Mood", latest_memory.get("mood_today")))
            _append_unique(lines, seen, self._field("Energy", latest_memory.get("energy_level")))
            _append_unique(lines, seen, self._field("Workload", latest_memory.get("workload_intensity")))
            _append_unique(lines, seen, self._field("Recovery status", latest_memory.get("recovery_status")))

        environment_rows = _as_list(daily_data.get("daily_environment_data"))
        if environment_rows and isinstance(environment_rows[0], dict):
            env = environment_rows[0]
            _append_unique(
                lines,
                seen,
                "Environment "
                f"({env.get('created_at', env.get('log_date', 'recent'))}): "
                f"AQI {env.get('aqi', 'N/A')}, "
                f"temperature {env.get('temperature_c', 'N/A')}C, "
                f"humidity {env.get('humidity_percent', 'N/A')}%, "
                f"UV {env.get('uv_index', 'N/A')}, "
                f"pollen {env.get('pollen_level', 'N/A')}, "
                f"outdoor hours {env.get('outdoor_hours', 'N/A')}.",
            )

        device_rows = _as_list(daily_data.get("daily_device_behavior_data"))
        if device_rows and isinstance(device_rows[0], dict):
            device = device_rows[0]
            _append_unique(
                lines,
                seen,
                "Device behavior: "
                f"screen time {device.get('screen_time_hours', 'N/A')}h, "
                f"late night usage {device.get('late_night_usage', 'N/A')}, "
                f"continuous usage {device.get('continuous_usage_minutes', 'N/A')} min.",
            )

        calendar_rows = _as_list(daily_data.get("daily_calendar_data"))
        if calendar_rows and isinstance(calendar_rows[0], dict):
            calendar = calendar_rows[0]
            _append_unique(
                lines,
                seen,
                "Schedule context: "
                f"travel {calendar.get('travel_event', 'N/A')}, "
                f"exam {calendar.get('exam_event', 'N/A')}, "
                f"workload {calendar.get('meetings_workload', 'N/A')}, "
                f"sleep disruption {calendar.get('sleep_schedule_disruption', 'N/A')}.",
            )

        if not lines:
            return ""

        body = _truncate_words("\n".join(lines), self.max_daily_tokens)
        return "# RECENT HEALTH CONTEXT (last 7 days)\n" + body

    def _build_hypothesis_block(self, hypotheses: list[dict[str, Any]]) -> str:
        valid = [
            hypothesis
            for hypothesis in hypotheses
            if hypothesis.get("cause") and isinstance(hypothesis.get("probability", 0), (int, float))
        ]
        if not valid:
            return ""

        lines = []
        for hypothesis in sorted(valid, key=lambda item: item["probability"], reverse=True)[:3]:
            probability = max(0.0, min(float(hypothesis["probability"]), 1.0))
            evidence = _join_list(hypothesis.get("evidence"))
            evidence_text = f", evidence: {evidence}" if evidence else ""
            lines.append(
                f"- {hypothesis['cause']} (probability: {probability:.0%}, "
                f"confidence: {hypothesis.get('confidence', 'low')}{evidence_text})"
            )

        body = _truncate_words("\n".join(lines), self.max_hypothesis_tokens)
        return "# ACTIVE HYPOTHESES\n" + body

    def _build_follow_up_block(self, follow_up_queue: list[str]) -> str:
        if follow_up_queue:
            instruction = f"Ask this question next (and only this one): {follow_up_queue[0]}"
        else:
            instruction = DEFAULT_FOLLOW_UP

        body = _truncate_words(instruction, self.max_follow_up_tokens)
        return "# FOLLOW-UP STRATEGY\n" + body

    def _fit_prompt(self, blocks: list[str]) -> str:
        prompt = "\n\n".join(blocks)
        if estimate_tokens(prompt) <= self.max_prompt_tokens:
            return prompt

        protected = blocks[0]
        remaining_budget = self.max_prompt_tokens - estimate_tokens(protected)
        if remaining_budget <= 0:
            return protected

        fitted_blocks = [protected]
        for block in blocks[1:]:
            block_tokens = estimate_tokens(block)
            if block_tokens <= remaining_budget:
                fitted_blocks.append(block)
                remaining_budget -= block_tokens
                continue
            if remaining_budget > 10:
                fitted_blocks.append(_truncate_words(block, remaining_budget))
            break

        return "\n\n".join(fitted_blocks)

    @staticmethod
    def _field(label: str, value: Any) -> str | None:
        if value in (None, "", []):
            return None
        return f"{label}: {value}"


def build_system_prompt(
    user_profile: dict[str, Any],
    daily_data: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    follow_up_queue: list[str],
) -> str:
    return PromptBuilder().build(
        user_profile=user_profile,
        daily_data=daily_data,
        hypotheses=hypotheses,
        follow_up_queue=follow_up_queue,
    )
