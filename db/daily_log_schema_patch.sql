-- VitaSense daily logging repair patch.
-- Run in Supabase SQL Editor if the Daily Routine save endpoint returns schema-cache errors.
-- This only adds missing columns/constraints required by the existing app schema.

do $$ begin
  create type public.overall_health_feeling_enum as enum ('Very Poor', 'Poor', 'Average', 'Good', 'Excellent');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.mood_today_enum as enum ('Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy', 'Anxious', 'Stressed', 'Exhausted');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.energy_level_enum as enum ('Very Low', 'Low', 'Moderate', 'Good', 'High');
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
  create type public.workload_intensity_enum as enum ('Very Low', 'Low', 'Moderate', 'High', 'Extreme');
exception when duplicate_object then null; end $$;

alter table public.daily_fitness_data add column if not exists log_date date not null default current_date;
alter table public.daily_fitness_data add column if not exists steps integer;
alter table public.daily_fitness_data add column if not exists distance_km numeric;
alter table public.daily_fitness_data add column if not exists calories_burned numeric;
alter table public.daily_fitness_data add column if not exists exercise_minutes integer;
alter table public.daily_fitness_data add column if not exists heart_rate_avg numeric;
alter table public.daily_fitness_data add column if not exists hrv_ms numeric;
alter table public.daily_fitness_data add column if not exists spo2_percent numeric;
alter table public.daily_fitness_data add column if not exists sleep_hours numeric;
alter table public.daily_fitness_data add column if not exists sleep_quality_score numeric;
alter table public.daily_fitness_data add column if not exists sleep_start_time timestamptz;
alter table public.daily_fitness_data add column if not exists sleep_end_time timestamptz;
alter table public.daily_fitness_data add column if not exists weight_kg numeric;
alter table public.daily_fitness_data add column if not exists water_ml integer;
alter table public.daily_fitness_data add column if not exists overall_health_feeling public.overall_health_feeling_enum;
alter table public.daily_fitness_data add column if not exists created_at timestamptz not null default now();

alter table public.daily_environment_data add column if not exists log_date date not null default current_date;
alter table public.daily_environment_data add column if not exists location text;
alter table public.daily_environment_data add column if not exists temperature_c numeric;
alter table public.daily_environment_data add column if not exists humidity_percent numeric;
alter table public.daily_environment_data add column if not exists aqi numeric;
alter table public.daily_environment_data add column if not exists uv_index numeric;
alter table public.daily_environment_data add column if not exists pollen_level text;
alter table public.daily_environment_data add column if not exists outdoor_hours numeric;
alter table public.daily_environment_data add column if not exists heatwave_alert boolean not null default false;
alter table public.daily_environment_data add column if not exists created_at timestamptz not null default now();

alter table public.daily_device_behavior_data add column if not exists log_date date not null default current_date;
alter table public.daily_device_behavior_data add column if not exists screen_time_hours numeric;
alter table public.daily_device_behavior_data add column if not exists late_night_usage boolean;
alter table public.daily_device_behavior_data add column if not exists continuous_usage_minutes integer;
alter table public.daily_device_behavior_data add column if not exists average_daily_usage_hours numeric;
alter table public.daily_device_behavior_data add column if not exists created_at timestamptz not null default now();

alter table public.daily_calendar_data add column if not exists log_date date not null default current_date;
alter table public.daily_calendar_data add column if not exists travel_event boolean;
alter table public.daily_calendar_data add column if not exists trip_duration_days integer;
alter table public.daily_calendar_data add column if not exists meetings_workload text;
alter table public.daily_calendar_data add column if not exists exam_event boolean;
alter table public.daily_calendar_data add column if not exists sleep_schedule_disruption boolean;
alter table public.daily_calendar_data add column if not exists created_at timestamptz not null default now();

alter table public.daily_user_memory_logs add column if not exists log_date date not null default current_date;
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
alter table public.daily_user_memory_logs add column if not exists created_at timestamptz not null default now();

do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'daily_fitness_data_user_id_log_date_key') then
    alter table public.daily_fitness_data add constraint daily_fitness_data_user_id_log_date_key unique (user_id, log_date);
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'daily_environment_data_user_id_log_date_key') then
    alter table public.daily_environment_data add constraint daily_environment_data_user_id_log_date_key unique (user_id, log_date);
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'daily_device_behavior_data_user_id_log_date_key') then
    alter table public.daily_device_behavior_data add constraint daily_device_behavior_data_user_id_log_date_key unique (user_id, log_date);
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'daily_calendar_data_user_id_log_date_key') then
    alter table public.daily_calendar_data add constraint daily_calendar_data_user_id_log_date_key unique (user_id, log_date);
  end if;
end $$;

do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'daily_user_memory_logs_user_id_log_date_key') then
    alter table public.daily_user_memory_logs add constraint daily_user_memory_logs_user_id_log_date_key unique (user_id, log_date);
  end if;
end $$;

create index if not exists idx_daily_fitness_user_date on public.daily_fitness_data(user_id, log_date desc);
create index if not exists idx_daily_environment_user_date on public.daily_environment_data(user_id, log_date desc);
create index if not exists idx_daily_device_user_date on public.daily_device_behavior_data(user_id, log_date desc);
create index if not exists idx_daily_calendar_user_date on public.daily_calendar_data(user_id, log_date desc);
create index if not exists idx_daily_memory_user_date on public.daily_user_memory_logs(user_id, log_date desc);
