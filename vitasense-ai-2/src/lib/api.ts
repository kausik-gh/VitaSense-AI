export type WellnessTrend = 'below_baseline' | 'near_baseline' | 'above_baseline' | 'unknown';
export type AlertSeverity = 'low' | 'medium' | 'high';

export interface WellnessMetric {
  label: string;
  value: number | null;
  baseline: number | null;
  unit: string;
  trend: WellnessTrend;
}

export interface WellnessForecast {
  user_id: number;
  date: string;
  headline: string;
  summary: string;
  readiness_score: number;
  energy: {
    score: number;
    state: string;
    trend: WellnessTrend;
  };
  recovery: {
    score: number;
    state: string;
    trend: WellnessTrend;
  };
  patterns: Array<{
    title: string;
    detail: string;
  }>;
  suggested_actions: Array<{
    title: string;
    detail: string;
  }>;
  environmental_alerts: Array<{
    type: string;
    severity: AlertSeverity;
    title: string;
    detail: string;
  }>;
  metrics: Record<string, WellnessMetric>;
  source_tables: string[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export type DailyEnergyLevel = 'Very Low' | 'Low' | 'Moderate' | 'Good' | 'High';
export type DailyMood =
  | 'Very Sad'
  | 'Sad'
  | 'Neutral'
  | 'Happy'
  | 'Very Happy'
  | 'Anxious'
  | 'Stressed'
  | 'Exhausted';
export type DailyOverallHealth = 'Very Poor' | 'Poor' | 'Average' | 'Good' | 'Excellent';
export type DailyWorkload = 'Very Low' | 'Low' | 'Moderate' | 'High' | 'Extreme';
export type DailySymptomSeverity = 'Mild' | 'Moderate' | 'Severe' | 'Critical';
export type DailyRiskLevel = 'Low' | 'Medium' | 'High' | 'Critical';
export type DailyRecoveryStatus = 'Recovering' | 'Recovered' | 'Not Improved' | 'Worsening';

export interface DailyLogPayload {
  log_date: string;
  manual: {
    breakfast_log: string | null;
    lunch_log: string | null;
    dinner_log: string | null;
    snacks_beverages_log: string | null;
    ate_from_outside: boolean | null;
    processed_food_consumed: boolean | null;
    unusual_food_exposure: boolean | null;
    unusual_exposure_notes: string | null;
    energy_level: DailyEnergyLevel | null;
    mood_today: DailyMood | null;
    overall_mental_feeling: DailyMood | null;
    emotional_physical_impact: boolean | null;
    physical_discomfort_notes: string | null;
    unusual_body_observation: string | null;
    daily_events: string[];
    workload_intensity: DailyWorkload | null;
    crowded_place_exposure: boolean | null;
    travel_today: boolean | null;
    emotional_event_notes: string | null;
    chatbot_symptoms_reported: string[];
    doctor_consulted_today: boolean | null;
    medical_visit_reason: string | null;
  };
}

export interface DailyLogResponse {
  user_id: number;
  log_date: string;
  saved_tables: string[];
  tables: Record<string, Record<string, unknown>>;
}

export interface SetupContextPayload {
  life_phase: string | null;
  social_environment: string | null;
  life_structure_type: string | null;
  lifestyle_identity: string | null;
  preferred_environment: string | null;
  perceived_health_triggers: string[];
  chronic_conditions: string[];
  recurring_health_patterns: string[];
  allergy_conditions: string[];
  major_medical_history: string[];
  personal_health_note: string | null;
  eating_behavior: string | null;
  unhealthy_eating_triggers: string[];
  body_awareness_level: string | null;
  emotional_health_impact: boolean | null;
  emotional_tracking_enabled: boolean;
  emotional_pressure_sources: string[];
  stress_response_pattern: string | null;
  recovery_preference: string | null;
}

export async function fetchWellnessForecast(userId: number, signal?: AbortSignal): Promise<WellnessForecast> {
  const response = await fetch(`${API_BASE_URL}/api/v1/user/${userId}/wellness-forecast`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Wellness forecast request failed with status ${response.status}`);
  }

  return response.json() as Promise<WellnessForecast>;
}

export async function fetchDailyLog(userId: number, logDate: string, signal?: AbortSignal): Promise<DailyLogResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/user/${userId}/daily-log?log_date=${logDate}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Daily log request failed with status ${response.status}`);
  }

  return response.json() as Promise<DailyLogResponse>;
}

export async function saveDailyLog(userId: number, payload: DailyLogPayload): Promise<DailyLogResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/user/${userId}/daily-log`, {
    method: 'PUT',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Daily log save failed with status ${response.status}`);
  }

  return response.json() as Promise<DailyLogResponse>;
}

export async function saveSetupContext(userId: number, payload: SetupContextPayload): Promise<{ user_id: number; saved_tables: string[] }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/user/${userId}/setup-context`, {
    method: 'PUT',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Setup context save failed with status ${response.status}`);
  }

  return response.json() as Promise<{ user_id: number; saved_tables: string[] }>;
}
