-- VitaSense / VitalIQ Health Chatbot schema
-- Run in Supabase SQL Editor for the target project.
-- Idempotent for fresh or partially-created projects.

create extension if not exists vector;

do $$ begin
  create type public.energy_level_enum as enum ('Very Low', 'Low', 'Moderate', 'Good', 'High');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.mood_today_enum as enum ('Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy', 'Anxious', 'Stressed', 'Exhausted');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.overall_health_feeling_enum as enum ('Very Poor', 'Poor', 'Average', 'Good', 'Excellent');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.workload_intensity_enum as enum ('Very Low', 'Low', 'Moderate', 'High', 'Extreme');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.chatbot_symptom_severity_enum as enum ('Mild', 'Moderate', 'Severe', 'Critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.chatbot_risk_level_enum as enum ('Low', 'Medium', 'High', 'Critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.recovery_status_enum as enum ('Recovering', 'Recovered', 'Not Improved', 'Worsening');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.life_phase_enum as enum ('Student Life', 'Early Career', 'High-Pressure Work Life', 'Transition Phase', 'Family-Focused Life', 'Irregular Lifestyle');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.social_environment_enum as enum ('Family', 'Friends/Roommates', 'Mostly Alone', 'Hostel Community', 'Coworkers/Classmates', 'Mixed');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.life_structure_type_enum as enum ('Highly Structured', 'Moderately Structured', 'Unpredictable', 'Chaotic');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.lifestyle_identity_enum as enum ('Health Conscious', 'Balanced', 'Stress-Driven', 'Highly Busy', 'Physically Active', 'Mentally Exhausted', 'Irregular Lifestyle');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.preferred_environment_enum as enum ('Cold Climate', 'Warm Climate', 'Dry Climate', 'Nature/Outdoors', 'Indoor Controlled Environment', 'No Specific Preference');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.eating_behavior_enum as enum ('Disciplined', 'Emotional Eating', 'Irregular Eating', 'Convenience-Based', 'Late-Night Eating', 'Stress-Based Eating');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.body_awareness_level_enum as enum ('Very Aware', 'Aware', 'Moderate', 'Low Awareness');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.stress_response_pattern_enum as enum ('Sleep', 'Appetite', 'Energy Levels', 'Mood', 'Focus', 'Physical Symptoms', 'Everything');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.recovery_preference_enum as enum ('Rest', 'Talking to Someone', 'Isolation', 'Exercise', 'Entertainment', 'Sleep', 'Food', 'Nature/Travel');
exception when duplicate_object then null; end $$;

create table if not exists public.users (
  id serial primary key,
  user_code text unique,
  name text,
  created_at timestamptz not null default now()
);

create table if not exists public.user_life_context (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  life_phase public.life_phase_enum,
  social_environment public.social_environment_enum,
  life_structure_type public.life_structure_type_enum,
  lifestyle_identity public.lifestyle_identity_enum,
  preferred_environment public.preferred_environment_enum,
  perceived_health_triggers text[] not null default '{}',
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_food_body_relationship (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  eating_behavior public.eating_behavior_enum,
  unhealthy_eating_triggers text[] not null default '{}',
  body_awareness_level public.body_awareness_level_enum,
  emotional_health_impact boolean,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_medical_identity (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  chronic_conditions text[] not null default '{}',
  recurring_health_patterns text[] not null default '{}',
  allergy_conditions text[] not null default '{}',
  major_medical_history text[] not null default '{}',
  personal_health_note text,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_emotional_wellness (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  emotional_tracking_enabled boolean not null default false,
  emotional_pressure_sources text[] not null default '{}',
  stress_response_pattern public.stress_response_pattern_enum,
  recovery_preference public.recovery_preference_enum,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_personal_context (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  personal_context_summary text,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_health_record_imports (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  health_reports jsonb not null default '[]'::jsonb,
  prescription_records jsonb not null default '[]'::jsonb,
  surgery_hospital_records jsonb not null default '[]'::jsonb,
  diagnosis_scan_reports jsonb not null default '[]'::jsonb,
  long_term_medical_note text,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.daily_fitness_data (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  log_date date not null default current_date,
  steps integer,
  distance_km numeric,
  calories_burned numeric,
  exercise_minutes integer,
  heart_rate_avg numeric,
  hrv_ms numeric,
  spo2_percent numeric,
  sleep_hours numeric,
  sleep_quality_score numeric,
  sleep_start_time timestamptz,
  sleep_end_time timestamptz,
  weight_kg numeric,
  water_ml integer,
  overall_health_feeling public.overall_health_feeling_enum,
  created_at timestamptz not null default now(),
  unique (user_id, log_date)
);

create table if not exists public.daily_environment_data (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  log_date date not null default current_date,
  location text,
  temperature_c numeric,
  humidity_percent numeric,
  aqi numeric,
  uv_index numeric,
  pollen_level text,
  outdoor_hours numeric,
  heatwave_alert boolean not null default false,
  created_at timestamptz not null default now(),
  unique (user_id, log_date)
);

create table if not exists public.daily_device_behavior_data (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  log_date date not null default current_date,
  screen_time_hours numeric,
  late_night_usage boolean,
  continuous_usage_minutes integer,
  average_daily_usage_hours numeric,
  created_at timestamptz not null default now(),
  unique (user_id, log_date)
);

create table if not exists public.daily_calendar_data (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  log_date date not null default current_date,
  travel_event boolean,
  trip_duration_days integer,
  meetings_workload text,
  exam_event boolean,
  sleep_schedule_disruption boolean,
  created_at timestamptz not null default now(),
  unique (user_id, log_date)
);

create table if not exists public.daily_user_memory_logs (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  log_date date not null default current_date,
  breakfast text,
  lunch text,
  dinner text,
  snacks text,
  food_flags text[] not null default '{}',
  mood_today public.mood_today_enum,
  energy_level public.energy_level_enum,
  symptom_today text[] not null default '{}',
  chatbot_symptoms text[] not null default '{}',
  chatbot_symptom_severity public.chatbot_symptom_severity_enum,
  chatbot_risk_level public.chatbot_risk_level_enum,
  doctor_visit boolean,
  personal_daily_note text,
  recovery_status public.recovery_status_enum,
  linked_medical_reports text[] not null default '{}',
  workload_intensity public.workload_intensity_enum,
  events text[] not null default '{}',
  created_at timestamptz not null default now(),
  unique (user_id, log_date)
);

create table if not exists public.ai_user_health_profile (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  ai_health_summary text,
  ai_behavioral_patterns text[] not null default '{}',
  ai_risk_factors text[] not null default '{}',
  ai_lifestyle_assessment text,
  ai_last_updated timestamptz,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.ai_health_insights (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  insight_title text,
  insight_description text,
  insight_type text,
  risk_level public.chatbot_risk_level_enum,
  generated_on date not null default current_date,
  created_at timestamptz not null default now()
);

create table if not exists public.chatbot_conversation_history (
  id bigserial primary key,
  user_id integer not null references public.users(id) on delete cascade,
  session_id text not null,
  message_role text not null check (message_role in ('system', 'user', 'assistant', 'tool')),
  message_content text not null,
  related_symptoms text[] not null default '{}',
  ai_risk_level public.chatbot_risk_level_enum,
  created_at timestamptz not null default now()
);

create index if not exists idx_user_life_context_user_id on public.user_life_context(user_id);
create index if not exists idx_user_food_body_relationship_user_id on public.user_food_body_relationship(user_id);
create index if not exists idx_user_medical_identity_user_id on public.user_medical_identity(user_id);
create index if not exists idx_user_emotional_wellness_user_id on public.user_emotional_wellness(user_id);
create index if not exists idx_user_personal_context_user_id on public.user_personal_context(user_id);
create index if not exists idx_ai_user_health_profile_user_id on public.ai_user_health_profile(user_id);
create index if not exists idx_daily_fitness_user_date on public.daily_fitness_data(user_id, log_date desc);
create index if not exists idx_daily_environment_user_created on public.daily_environment_data(user_id, created_at desc);
create index if not exists idx_daily_device_user_created on public.daily_device_behavior_data(user_id, created_at desc);
create index if not exists idx_daily_calendar_user_created on public.daily_calendar_data(user_id, created_at desc);
create index if not exists idx_daily_memory_user_created on public.daily_user_memory_logs(user_id, created_at desc);
create index if not exists idx_chatbot_history_user_created on public.chatbot_conversation_history(user_id, created_at desc);
create index if not exists idx_chatbot_history_user_session on public.chatbot_conversation_history(user_id, session_id);

alter table public.users enable row level security;
alter table public.user_life_context enable row level security;
alter table public.user_food_body_relationship enable row level security;
alter table public.user_medical_identity enable row level security;
alter table public.user_emotional_wellness enable row level security;
alter table public.user_personal_context enable row level security;
alter table public.user_health_record_imports enable row level security;
alter table public.daily_fitness_data enable row level security;
alter table public.daily_environment_data enable row level security;
alter table public.daily_device_behavior_data enable row level security;
alter table public.daily_calendar_data enable row level security;
alter table public.daily_user_memory_logs enable row level security;
alter table public.ai_user_health_profile enable row level security;
alter table public.ai_health_insights enable row level security;
alter table public.chatbot_conversation_history enable row level security;

insert into public.users (id, user_code, name)
values (1, 'demo-user', 'Samantha W.')
on conflict (id) do nothing;

insert into public.user_life_context (
  user_id,
  life_phase,
  social_environment,
  life_structure_type,
  lifestyle_identity,
  preferred_environment,
  perceived_health_triggers
) values (
  1,
  'Early Career',
  'Mostly Alone',
  'Moderately Structured',
  'Highly Busy',
  'Indoor Controlled Environment',
  array['poor sleep', 'high workload', 'pollution']
) on conflict (user_id) do nothing;

insert into public.user_medical_identity (
  user_id,
  chronic_conditions,
  recurring_health_patterns,
  allergy_conditions,
  major_medical_history,
  personal_health_note
) values (
  1,
  array[]::text[],
  array['throat irritation during poor AQI', 'fatigue after low sleep'],
  array['pollen'],
  array[]::text[],
  'Demo profile for VitaSense local verification.'
) on conflict (user_id) do nothing;

insert into public.daily_fitness_data (
  user_id,
  log_date,
  steps,
  exercise_minutes,
  heart_rate_avg,
  hrv_ms,
  spo2_percent,
  sleep_hours,
  sleep_quality_score,
  water_ml
) values
  (1, current_date, 3100, 10, 78, 35, 98, 5.5, 62, 1100),
  (1, current_date - interval '1 day', 6200, 28, 72, 48, 98, 7.2, 82, 2200),
  (1, current_date - interval '2 days', 5900, 24, 73, 50, 99, 7.0, 80, 2100)
on conflict (user_id, log_date) do nothing;

insert into public.daily_environment_data (
  user_id,
  log_date,
  location,
  temperature_c,
  humidity_percent,
  aqi,
  uv_index,
  pollen_level,
  outdoor_hours,
  heatwave_alert
) values (
  1,
  current_date,
  'Demo City',
  34,
  70,
  162,
  8,
  'High',
  2,
  false
) on conflict (user_id, log_date) do nothing;

insert into public.daily_device_behavior_data (
  user_id,
  log_date,
  screen_time_hours,
  late_night_usage,
  continuous_usage_minutes,
  average_daily_usage_hours
) values (
  1,
  current_date,
  8.5,
  true,
  95,
  7.8
) on conflict (user_id, log_date) do nothing;

insert into public.daily_calendar_data (
  user_id,
  log_date,
  travel_event,
  trip_duration_days,
  meetings_workload,
  exam_event,
  sleep_schedule_disruption
) values (
  1,
  current_date,
  false,
  null,
  'High',
  false,
  true
) on conflict (user_id, log_date) do nothing;

insert into public.daily_user_memory_logs (
  user_id,
  log_date,
  breakfast,
  lunch,
  dinner,
  snacks,
  mood_today,
  energy_level,
  symptom_today,
  chatbot_symptoms,
  recovery_status,
  workload_intensity,
  events
) values (
  1,
  current_date,
  'toast',
  'rice bowl',
  'late noodles',
  'chips',
  'Stressed',
  'Low',
  array['fatigue'],
  array['fatigue'],
  'Recovering',
  'High',
  array['long work block']
) on conflict (user_id, log_date) do nothing;
