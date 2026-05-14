-- VitaSense schema repair patch for partially-created Supabase projects.
-- Run this after db/supabase_schema.sql if some tables/columns already existed.
-- It adds missing backend-required tables/columns without deleting data.

create table if not exists public.users (
  id serial primary key,
  user_code text unique,
  name text,
  created_at timestamptz not null default now()
);

insert into public.users (id, user_code, name)
values (1, 'demo-user', 'Samantha W.')
on conflict (id) do nothing;

create table if not exists public.user_food_body_relationship (
  id bigserial primary key,
  user_id integer not null,
  eating_behavior public.eating_behavior_enum,
  unhealthy_eating_triggers text[] not null default '{}',
  body_awareness_level public.body_awareness_level_enum,
  emotional_health_impact boolean,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_emotional_wellness (
  id bigserial primary key,
  user_id integer not null,
  emotional_tracking_enabled boolean not null default false,
  emotional_pressure_sources text[] not null default '{}',
  stress_response_pattern public.stress_response_pattern_enum,
  recovery_preference public.recovery_preference_enum,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.user_personal_context (
  id bigserial primary key,
  user_id integer not null,
  personal_context_summary text,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.ai_user_health_profile (
  id bigserial primary key,
  user_id integer not null,
  ai_health_summary text,
  ai_behavioral_patterns text[] not null default '{}',
  ai_risk_factors text[] not null default '{}',
  ai_lifestyle_assessment text,
  ai_last_updated timestamptz,
  created_at timestamptz not null default now(),
  unique (user_id)
);

create table if not exists public.chatbot_conversation_history (
  id bigserial primary key,
  user_id integer not null,
  session_id text not null,
  message_role text not null check (message_role in ('system', 'user', 'assistant', 'tool')),
  message_content text not null,
  related_symptoms text[] not null default '{}',
  ai_risk_level public.chatbot_risk_level_enum,
  created_at timestamptz not null default now()
);

alter table public.user_life_context add column if not exists created_at timestamptz not null default now();
alter table public.user_medical_identity add column if not exists created_at timestamptz not null default now();
alter table public.daily_fitness_data add column if not exists created_at timestamptz not null default now();
alter table public.daily_environment_data add column if not exists created_at timestamptz not null default now();
alter table public.daily_device_behavior_data add column if not exists created_at timestamptz not null default now();
alter table public.daily_calendar_data add column if not exists created_at timestamptz not null default now();
alter table public.daily_user_memory_logs add column if not exists created_at timestamptz not null default now();

alter table public.daily_environment_data add column if not exists aqi numeric;
alter table public.daily_environment_data add column if not exists temperature_c numeric;
alter table public.daily_environment_data add column if not exists humidity_percent numeric;
alter table public.daily_environment_data add column if not exists uv_index numeric;
alter table public.daily_environment_data add column if not exists pollen_level text;
alter table public.daily_environment_data add column if not exists outdoor_hours numeric;
alter table public.daily_environment_data add column if not exists heatwave_alert boolean not null default false;

alter table public.daily_device_behavior_data add column if not exists screen_time_hours numeric;
alter table public.daily_device_behavior_data add column if not exists late_night_usage boolean;
alter table public.daily_device_behavior_data add column if not exists continuous_usage_minutes integer;
alter table public.daily_device_behavior_data add column if not exists average_daily_usage_hours numeric;

alter table public.daily_calendar_data add column if not exists travel_event boolean;
alter table public.daily_calendar_data add column if not exists trip_duration_days integer;
alter table public.daily_calendar_data add column if not exists meetings_workload text;
alter table public.daily_calendar_data add column if not exists exam_event boolean;
alter table public.daily_calendar_data add column if not exists sleep_schedule_disruption boolean;

alter table public.daily_user_memory_logs add column if not exists breakfast text;
alter table public.daily_user_memory_logs add column if not exists lunch text;
alter table public.daily_user_memory_logs add column if not exists dinner text;
alter table public.daily_user_memory_logs add column if not exists snacks text;
alter table public.daily_user_memory_logs add column if not exists food_flags text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists mood_today public.mood_today_enum;
alter table public.daily_user_memory_logs add column if not exists energy_level public.energy_level_enum;
alter table public.daily_user_memory_logs add column if not exists symptom_today text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_symptoms text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_symptom_severity public.chatbot_symptom_severity_enum;
alter table public.daily_user_memory_logs add column if not exists chatbot_risk_level public.chatbot_risk_level_enum;
alter table public.daily_user_memory_logs add column if not exists doctor_visit boolean;
alter table public.daily_user_memory_logs add column if not exists personal_daily_note text;
alter table public.daily_user_memory_logs add column if not exists recovery_status public.recovery_status_enum;
alter table public.daily_user_memory_logs add column if not exists linked_medical_reports text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists workload_intensity public.workload_intensity_enum;
alter table public.daily_user_memory_logs add column if not exists events text[] not null default '{}';

create index if not exists idx_daily_environment_user_created on public.daily_environment_data(user_id, created_at desc);
create index if not exists idx_daily_device_user_created on public.daily_device_behavior_data(user_id, created_at desc);
create index if not exists idx_daily_calendar_user_created on public.daily_calendar_data(user_id, created_at desc);
create index if not exists idx_daily_memory_user_created on public.daily_user_memory_logs(user_id, created_at desc);
create index if not exists idx_chatbot_history_user_created on public.chatbot_conversation_history(user_id, created_at desc);
create index if not exists idx_chatbot_history_user_session on public.chatbot_conversation_history(user_id, session_id);

insert into public.user_food_body_relationship (
  user_id,
  eating_behavior,
  unhealthy_eating_triggers,
  body_awareness_level,
  emotional_health_impact
) values (
  1,
  'Irregular Eating',
  array['late work', 'stress'],
  'Aware',
  true
) on conflict (user_id) do nothing;

insert into public.user_emotional_wellness (
  user_id,
  emotional_tracking_enabled,
  emotional_pressure_sources,
  stress_response_pattern,
  recovery_preference
) values (
  1,
  true,
  array['workload', 'sleep disruption'],
  'Sleep',
  'Rest'
) on conflict (user_id) do nothing;

insert into public.user_personal_context (
  user_id,
  personal_context_summary
) values (
  1,
  'Usually works late during release weeks and is sensitive to poor sleep.'
) on conflict (user_id) do nothing;

insert into public.ai_user_health_profile (
  user_id,
  ai_health_summary,
  ai_behavioral_patterns,
  ai_risk_factors,
  ai_lifestyle_assessment,
  ai_last_updated
) values (
  1,
  'Sleep dips and workload spikes often precede lower energy.',
  array['low sleep before high workload', 'hydration drift during busy days'],
  array['low hydration', 'late night screen time', 'poor AQI sensitivity'],
  'Highly busy lifestyle with recovery needs concentrated around sleep and hydration.',
  now()
) on conflict (user_id) do nothing;
