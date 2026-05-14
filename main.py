import logging
import uuid
import asyncio
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from chat.orchestrator import OrchestratorDependencies, stream_chat_sse
from db.daily_log_store import build_automatic_daily_payloads, fetch_daily_log, upsert_daily_log_tables
from db.setup_context_store import upsert_setup_context_tables
from db.supabase_client import get_supabase
from db.user_context_loader import load_recent_daily_data, load_user_health_context
from grok_client import GrokClient
from logging_config import configure_logging
from state.conversation_store import conversation_store
from wellness.forecast import build_wellness_forecast

load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)

HISTORY_QUERY_TIMEOUT_SECONDS = 10.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    grok_client: GrokClient | None = None
    try:
        grok_client = GrokClient()
        models = await grok_client.verify_models()
        app.state.grok_client = grok_client
        logger.info("Application startup completed; Grok models verified", extra={"model_count": len(models)})
        yield
    except Exception:
        logger.critical("Application startup failed")
        raise
    finally:
        if grok_client is not None:
            await grok_client.close()


app = FastAPI(
    title="VitalIQ Health Chatbot",
    version="2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

EnergyLevel = Literal["Very Low", "Low", "Moderate", "Good", "High"]
MoodToday = Literal["Very Sad", "Sad", "Neutral", "Happy", "Very Happy", "Anxious", "Stressed", "Exhausted"]
WorkloadIntensity = Literal["Very Low", "Low", "Moderate", "High", "Extreme"]
RiskLevel = Literal["Low", "Medium", "High", "Critical"]
LifePhase = Literal["Student Life", "Early Career", "High-Pressure Work Life", "Transition Phase", "Family-Focused Life", "Irregular Lifestyle"]
SocialEnvironment = Literal["Family", "Friends/Roommates", "Mostly Alone", "Hostel Community", "Coworkers/Classmates", "Mixed"]
LifeStructureType = Literal["Highly Structured", "Moderately Structured", "Unpredictable", "Chaotic"]
LifestyleIdentity = Literal["Health Conscious", "Balanced", "Stress-Driven", "Highly Busy", "Physically Active", "Mentally Exhausted", "Irregular Lifestyle"]
PreferredEnvironment = Literal["Cold Climate", "Warm Climate", "Dry Climate", "Nature/Outdoors", "Indoor Controlled Environment", "No Specific Preference"]
EatingBehavior = Literal["Disciplined", "Emotional Eating", "Irregular Eating", "Convenience-Based", "Late-Night Eating", "Stress-Based Eating"]
BodyAwarenessLevel = Literal["Very Aware", "Aware", "Moderate", "Low Awareness"]
StressResponsePattern = Literal["Sleep", "Appetite", "Energy Levels", "Mood", "Focus", "Physical Symptoms", "Everything"]
RecoveryPreference = Literal["Rest", "Talking to Someone", "Isolation", "Exercise", "Entertainment", "Sleep", "Food", "Nature/Travel"]


class ChatRequest(BaseModel):
    user_id: int = Field(gt=0)
    message: str = Field(min_length=1)
    session_id: str | None = Field(default=None, min_length=1)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty")
        return value


class HistoryResponse(BaseModel):
    history: list[dict[str, Any]]


class DailyManualInput(BaseModel):
    breakfast_log: str | None = Field(default=None, max_length=500)
    lunch_log: str | None = Field(default=None, max_length=500)
    dinner_log: str | None = Field(default=None, max_length=500)
    snacks_beverages_log: str | None = Field(default=None, max_length=500)
    ate_from_outside: bool | None = None
    processed_food_consumed: bool | None = None
    unusual_food_exposure: bool | None = None
    unusual_exposure_notes: str | None = Field(default=None, max_length=1000)
    energy_level: EnergyLevel | None = None
    mood_today: MoodToday | None = None
    overall_mental_feeling: MoodToday | None = None
    emotional_physical_impact: bool | None = None
    physical_discomfort_notes: str | None = Field(default=None, max_length=1000)
    unusual_body_observation: str | None = Field(default=None, max_length=1000)
    daily_events: list[str] = Field(default_factory=list, max_length=20)
    workload_intensity: WorkloadIntensity | None = None
    crowded_place_exposure: bool | None = None
    travel_today: bool | None = None
    emotional_event_notes: str | None = Field(default=None, max_length=1000)
    chatbot_symptoms_reported: list[str] = Field(default_factory=list, max_length=20)
    doctor_consulted_today: bool | None = None
    medical_visit_reason: str | None = Field(default=None, max_length=1000)

    @field_validator("daily_events", "chatbot_symptoms_reported")
    @classmethod
    def clean_text_array(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            normalized = item.strip()
            if normalized:
                cleaned.append(normalized[:120])
        return cleaned


class DailyLogRequest(BaseModel):
    log_date: date
    manual: DailyManualInput = Field(default_factory=DailyManualInput)


class DailyLogResponse(BaseModel):
    user_id: int
    log_date: str
    saved_tables: list[str] = Field(default_factory=list)
    tables: dict[str, dict[str, Any]]


class SetupContextRequest(BaseModel):
    life_phase: LifePhase | None = None
    social_environment: SocialEnvironment | None = None
    life_structure_type: LifeStructureType | None = None
    lifestyle_identity: LifestyleIdentity | None = None
    preferred_environment: PreferredEnvironment | None = None
    perceived_health_triggers: list[str] = Field(default_factory=list, max_length=30)
    chronic_conditions: list[str] = Field(default_factory=list, max_length=30)
    recurring_health_patterns: list[str] = Field(default_factory=list, max_length=30)
    allergy_conditions: list[str] = Field(default_factory=list, max_length=30)
    major_medical_history: list[str] = Field(default_factory=list, max_length=30)
    personal_health_note: str | None = Field(default=None, max_length=3000)
    eating_behavior: EatingBehavior | None = None
    unhealthy_eating_triggers: list[str] = Field(default_factory=list, max_length=30)
    body_awareness_level: BodyAwarenessLevel | None = None
    emotional_health_impact: bool | None = None
    emotional_tracking_enabled: bool = True
    emotional_pressure_sources: list[str] = Field(default_factory=list, max_length=30)
    stress_response_pattern: StressResponsePattern | None = None
    recovery_preference: RecoveryPreference | None = None

    @field_validator(
        "perceived_health_triggers",
        "chronic_conditions",
        "recurring_health_patterns",
        "allergy_conditions",
        "major_medical_history",
        "unhealthy_eating_triggers",
        "emotional_pressure_sources",
    )
    @classmethod
    def clean_setup_text_array(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            normalized = item.strip()
            if normalized:
                cleaned.append(normalized[:160])
        return cleaned


class SetupContextResponse(BaseModel):
    user_id: int
    saved_tables: list[str]


class WellnessForecastResponse(BaseModel):
    user_id: int
    date: str
    headline: str
    summary: str
    readiness_score: int
    energy: dict[str, Any]
    recovery: dict[str, Any]
    patterns: list[dict[str, str]]
    suggested_actions: list[dict[str, str]]
    environmental_alerts: list[dict[str, str]]
    metrics: dict[str, dict[str, Any]]
    source_tables: list[str]


@app.get("/health")
async def health(request: Request) -> dict[str, str | bool]:
    grok_client: GrokClient | None = getattr(request.app.state, "grok_client", None)
    grok_ok = False
    if grok_client is not None:
        grok_ok = await grok_client.health_check()

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "grok": grok_ok,
    }


def _get_dependencies(request: Request) -> OrchestratorDependencies:
    grok_client: GrokClient | None = getattr(request.app.state, "grok_client", None)
    if grok_client is None:
        raise HTTPException(status_code=503, detail="Grok client is not initialized")

    return OrchestratorDependencies(
        grok_client=grok_client,
        supabase_factory=get_supabase,
        store=conversation_store,
    )


def _daily_log_table_payloads(user_id: int, payload: DailyLogRequest) -> dict[str, dict[str, Any]]:
    table_payloads = build_automatic_daily_payloads(user_id=user_id, log_date=payload.log_date)
    manual = payload.manual.model_dump()
    ai_fields = _daily_ai_fields(payload.manual)
    table_payloads["daily_user_memory_logs"] = {
        **manual,
        "breakfast": manual.get("breakfast_log"),
        "lunch": manual.get("lunch_log"),
        "dinner": manual.get("dinner_log"),
        "snacks": manual.get("snacks_beverages_log"),
        "events": manual.get("daily_events", []),
        "chatbot_symptoms": manual.get("chatbot_symptoms_reported", []),
        "doctor_visit": manual.get("doctor_consulted_today"),
        **ai_fields,
    }
    return table_payloads


def _daily_ai_fields(manual: DailyManualInput) -> dict[str, Any]:
    symptoms = manual.chatbot_symptoms_reported
    context = [manual.physical_discomfort_notes, manual.unusual_body_observation, manual.emotional_event_notes]
    joined = " ".join(item.lower() for item in [*symptoms, *[value or "" for value in context]])
    risk_level: RiskLevel = "Medium" if any(word in joined for word in ("pain", "fever", "dizzy", "breath")) else "Low"
    if any(word in joined for word in ("severe", "chest", "faint", "emergency")):
        risk_level = "High"

    possible_causes = ["hydration, sleep, workload, food exposure, and environmental patterns"]
    if manual.processed_food_consumed or manual.ate_from_outside or manual.unusual_food_exposure:
        possible_causes.append("recent food exposure or meal timing")
    if manual.workload_intensity in {"High", "Extreme"} or manual.emotional_physical_impact:
        possible_causes.append("stress load and emotional-body response")

    return {
        "chatbot_possible_causes": possible_causes,
        "chatbot_health_assistant_response": (
            "VitaSense logged these signals for pattern tracking. If symptoms worsen or feel concerning, consult a qualified clinician."
        ),
        "chatbot_recommended_actions": [
            "Monitor changes through the day",
            "Prioritize hydration and rest",
            "Avoid intense activity if discomfort increases",
        ],
        "chatbot_risk_level": risk_level,
        "chatbot_followup_questions": [
            "When did this start?",
            "Is it improving, worsening, or staying the same?",
        ],
        "chatbot_session_summary": "Daily log captured with manual user context and generated assistant metadata.",
    }


def _setup_context_payloads(payload: SetupContextRequest) -> dict[str, dict[str, Any]]:
    personal_summary = _personal_context_summary(payload)
    ai_patterns = _ai_behavioral_patterns(payload)
    ai_risks = _ai_risk_factors(payload)
    return {
        "user_life_context": {
            "life_phase": payload.life_phase,
            "social_environment": payload.social_environment,
            "life_structure_type": payload.life_structure_type,
            "lifestyle_identity": payload.lifestyle_identity,
            "preferred_environment": payload.preferred_environment,
            "perceived_health_triggers": payload.perceived_health_triggers,
        },
        "user_medical_identity": {
            "chronic_conditions": payload.chronic_conditions,
            "recurring_health_patterns": payload.recurring_health_patterns,
            "allergy_conditions": payload.allergy_conditions,
            "major_medical_history": payload.major_medical_history,
            "personal_health_note": payload.personal_health_note,
        },
        "user_food_body_relationship": {
            "eating_behavior": payload.eating_behavior,
            "unhealthy_eating_triggers": payload.unhealthy_eating_triggers,
            "body_awareness_level": payload.body_awareness_level,
            "emotional_health_impact": payload.emotional_health_impact,
        },
        "user_emotional_wellness": {
            "emotional_tracking_enabled": payload.emotional_tracking_enabled,
            "emotional_pressure_sources": payload.emotional_pressure_sources,
            "stress_response_pattern": payload.stress_response_pattern,
            "recovery_preference": payload.recovery_preference,
        },
        "user_personal_context": {
            "personal_context_summary": personal_summary,
        },
        "ai_user_health_profile": {
            "ai_health_summary": f"{personal_summary} VitaSense should compare daily signals against this baseline.",
            "ai_behavioral_patterns": ai_patterns,
            "ai_risk_factors": ai_risks,
            "ai_lifestyle_assessment": _ai_lifestyle_assessment(payload),
            "ai_last_updated": datetime.now(timezone.utc).isoformat(),
        },
    }


def _personal_context_summary(payload: SetupContextRequest) -> str:
    parts = [
        payload.life_phase,
        payload.lifestyle_identity,
        payload.life_structure_type,
        payload.preferred_environment,
    ]
    summary = ", ".join(part for part in parts if part)
    if payload.personal_health_note:
        summary = f"{summary}. {payload.personal_health_note}" if summary else payload.personal_health_note
    return summary or "User setup context is available for personalization."


def _ai_behavioral_patterns(payload: SetupContextRequest) -> list[str]:
    patterns: list[str] = []
    if payload.perceived_health_triggers:
        patterns.append("Health often changes around: " + ", ".join(payload.perceived_health_triggers[:4]))
    if payload.unhealthy_eating_triggers:
        patterns.append("Eating behavior may shift around: " + ", ".join(payload.unhealthy_eating_triggers[:4]))
    if payload.emotional_pressure_sources:
        patterns.append("Emotional pressure sources include: " + ", ".join(payload.emotional_pressure_sources[:4]))
    return patterns or ["Initial behavioral baseline captured during onboarding."]


def _ai_risk_factors(payload: SetupContextRequest) -> list[str]:
    risks = [*payload.chronic_conditions, *payload.allergy_conditions, *payload.recurring_health_patterns]
    return risks[:8] or ["No explicit long-term risk factors reported during onboarding."]


def _ai_lifestyle_assessment(payload: SetupContextRequest) -> str:
    if payload.lifestyle_identity or payload.life_structure_type:
        return f"{payload.lifestyle_identity or 'Current lifestyle'} with {payload.life_structure_type or 'unknown structure'} routine."
    return "Lifestyle assessment will improve as daily logs accumulate."


@app.post("/api/v1/chat")
async def chat(request: Request, chat_request: ChatRequest) -> StreamingResponse:
    session_id = chat_request.session_id or str(uuid.uuid4())
    dependencies = _get_dependencies(request)

    return StreamingResponse(
        stream_chat_sse(
            chat_request.user_id,
            session_id,
            chat_request.message.strip(),
            dependencies=dependencies,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/v1/user/{user_id}/history", response_model=HistoryResponse)
async def get_history(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
) -> HistoryResponse:
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="user_id must be a positive integer")

    try:
        supabase = get_supabase()
    except Exception:
        logger.error("Supabase client initialization failed for history", extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="History storage is unavailable") from None

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: (
                    supabase.table("chatbot_conversation_history")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
            ),
            timeout=HISTORY_QUERY_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("History query timed out", extra={"user_id": user_id})
        raise HTTPException(status_code=504, detail="History query timed out") from None
    except Exception:
        logger.error("History query failed", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="History query failed") from None

    data = getattr(response, "data", None)
    history = data if isinstance(data, list) else []
    return HistoryResponse(history=history)


@app.get("/api/v1/user/{user_id}/daily-log", response_model=DailyLogResponse)
async def get_daily_log(
    user_id: int,
    log_date: date = Query(...),
) -> DailyLogResponse:
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="user_id must be a positive integer")

    try:
        supabase = get_supabase()
    except Exception:
        logger.error("Supabase client initialization failed for daily log load", extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="Daily log storage is unavailable") from None

    data = await fetch_daily_log(supabase, user_id=user_id, log_date=log_date)
    return DailyLogResponse(saved_tables=[], **data)


@app.put("/api/v1/user/{user_id}/daily-log", response_model=DailyLogResponse)
async def save_daily_log(user_id: int, daily_log: DailyLogRequest) -> DailyLogResponse:
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="user_id must be a positive integer")

    try:
        supabase = get_supabase()
    except Exception:
        logger.error("Supabase client initialization failed for daily log save", extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="Daily log storage is unavailable") from None

    try:
        saved_tables = await upsert_daily_log_tables(
            supabase,
            user_id=user_id,
            log_date=daily_log.log_date,
            table_payloads=_daily_log_table_payloads(user_id, daily_log),
        )
        data = await fetch_daily_log(supabase, user_id=user_id, log_date=daily_log.log_date)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Daily log save timed out") from None
    except Exception:
        raise HTTPException(status_code=500, detail="Daily log save failed") from None

    return DailyLogResponse(saved_tables=saved_tables, **data)


@app.put("/api/v1/user/{user_id}/setup-context", response_model=SetupContextResponse)
async def save_setup_context(user_id: int, setup_context: SetupContextRequest) -> SetupContextResponse:
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="user_id must be a positive integer")

    try:
        supabase = get_supabase()
    except Exception:
        logger.error("Supabase client initialization failed for setup context save", extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="Setup context storage is unavailable") from None

    try:
        saved_tables = await upsert_setup_context_tables(
            supabase,
            user_id=user_id,
            table_payloads=_setup_context_payloads(setup_context),
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Setup context save timed out") from None
    except Exception:
        raise HTTPException(status_code=500, detail="Setup context save failed") from None

    return SetupContextResponse(user_id=user_id, saved_tables=saved_tables)


@app.get("/api/v1/user/{user_id}/wellness-forecast", response_model=WellnessForecastResponse)
async def get_wellness_forecast(user_id: int) -> WellnessForecastResponse:
    if user_id <= 0:
        raise HTTPException(status_code=422, detail="user_id must be a positive integer")

    try:
        supabase = get_supabase()
    except Exception:
        logger.error("Supabase client initialization failed for wellness forecast", extra={"user_id": user_id})
        raise HTTPException(status_code=503, detail="Wellness forecast data is unavailable") from None

    try:
        user_profile, daily_data = await asyncio.gather(
            load_user_health_context(supabase, user_id),
            load_recent_daily_data(supabase, user_id, 7),
        )
    except Exception:
        logger.error("Wellness forecast context load failed", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="Wellness forecast context load failed") from None

    forecast = build_wellness_forecast(
        user_id=user_id,
        user_profile=user_profile,
        daily_data=daily_data,
    )
    return WellnessForecastResponse(**forecast)
