-- VitaSense data model upgrade.
-- Adds expanded automatic signals, daily manual logs, and setup-context compatibility.
-- Safe to run multiple times. Existing columns/data are preserved.

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
  create type public.chatbot_risk_level_enum as enum ('Low', 'Medium', 'High', 'Critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.workload_intensity_enum as enum ('Very Low', 'Low', 'Moderate', 'High', 'Extreme');
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

alter table public.daily_fitness_data add column if not exists log_date date not null default current_date;
alter table public.daily_fitness_data add column if not exists steps integer;
alter table public.daily_fitness_data add column if not exists sleep_walked integer;
alter table public.daily_fitness_data add column if not exists walking_distance_km numeric;
alter table public.daily_fitness_data add column if not exists distance_km numeric;
alter table public.daily_fitness_data add column if not exists calories_burned integer;
alter table public.daily_fitness_data add column if not exists exercise_duration_minutes integer;
alter table public.daily_fitness_data add column if not exists exercise_minutes integer;
alter table public.daily_fitness_data add column if not exists workout_type text;
alter table public.daily_fitness_data add column if not exists heart_rate_avg integer;
alter table public.daily_fitness_data add column if not exists resting_heart_rate integer;
alter table public.daily_fitness_data add column if not exists sedentary_time_hours numeric;
alter table public.daily_fitness_data add column if not exists active_hours numeric;
alter table public.daily_fitness_data add column if not exists sleep_duration_hours numeric;
alter table public.daily_fitness_data add column if not exists sleep_hours numeric;
alter table public.daily_fitness_data add column if not exists sleep_start_time time;
alter table public.daily_fitness_data add column if not exists sleep_end_time time;
alter table public.daily_fitness_data add column if not exists sleep_interruptions integer;
alter table public.daily_fitness_data add column if not exists hrv_score integer;
alter table public.daily_fitness_data add column if not exists hrv_ms numeric;
alter table public.daily_fitness_data add column if not exists spo2_level numeric;
alter table public.daily_fitness_data add column if not exists spo2_percent numeric;
alter table public.daily_fitness_data add column if not exists body_temperature numeric;
alter table public.daily_fitness_data add column if not exists water_intake_liters numeric;
alter table public.daily_fitness_data add column if not exists water_ml integer;
alter table public.daily_fitness_data add column if not exists body_weight_kg numeric;
alter table public.daily_fitness_data add column if not exists weight_kg numeric;
alter table public.daily_fitness_data add column if not exists overall_health_feeling public.overall_health_feeling_enum;
alter table public.daily_fitness_data add column if not exists created_at timestamptz not null default now();

do $$ begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'daily_fitness_data'
      and column_name = 'sleep_start_time'
      and data_type <> 'time without time zone'
  ) then
    alter table public.daily_fitness_data
      alter column sleep_start_time type time using sleep_start_time::time;
  end if;
end $$;

do $$ begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'daily_fitness_data'
      and column_name = 'sleep_end_time'
      and data_type <> 'time without time zone'
  ) then
    alter table public.daily_fitness_data
      alter column sleep_end_time type time using sleep_end_time::time;
  end if;
end $$;

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
alter table public.daily_user_memory_logs add column if not exists breakfast_log text;
alter table public.daily_user_memory_logs add column if not exists lunch_log text;
alter table public.daily_user_memory_logs add column if not exists dinner_log text;
alter table public.daily_user_memory_logs add column if not exists snacks_beverages_log text;
alter table public.daily_user_memory_logs add column if not exists breakfast text;
alter table public.daily_user_memory_logs add column if not exists lunch text;
alter table public.daily_user_memory_logs add column if not exists dinner text;
alter table public.daily_user_memory_logs add column if not exists snacks text;
alter table public.daily_user_memory_logs add column if not exists ate_from_outside boolean;
alter table public.daily_user_memory_logs add column if not exists processed_food_consumed boolean;
alter table public.daily_user_memory_logs add column if not exists unusual_food_exposure boolean;
alter table public.daily_user_memory_logs add column if not exists unusual_exposure_notes text;
alter table public.daily_user_memory_logs add column if not exists energy_level public.energy_level_enum;
alter table public.daily_user_memory_logs add column if not exists mood_today public.mood_today_enum;
alter table public.daily_user_memory_logs add column if not exists overall_mental_feeling public.mood_today_enum;
alter table public.daily_user_memory_logs add column if not exists emotional_physical_impact boolean;
alter table public.daily_user_memory_logs add column if not exists physical_discomfort_notes text;
alter table public.daily_user_memory_logs add column if not exists unusual_body_observation text;
alter table public.daily_user_memory_logs add column if not exists daily_events text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists events text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists workload_intensity public.workload_intensity_enum;
alter table public.daily_user_memory_logs add column if not exists crowded_place_exposure boolean;
alter table public.daily_user_memory_logs add column if not exists travel_today boolean;
alter table public.daily_user_memory_logs add column if not exists emotional_event_notes text;
alter table public.daily_user_memory_logs add column if not exists chatbot_symptoms_reported text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_symptoms text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_possible_causes text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_health_assistant_response text;
alter table public.daily_user_memory_logs add column if not exists chatbot_recommended_actions text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_risk_level public.chatbot_risk_level_enum;
alter table public.daily_user_memory_logs add column if not exists chatbot_followup_questions text[] not null default '{}';
alter table public.daily_user_memory_logs add column if not exists chatbot_session_summary text;
alter table public.daily_user_memory_logs add column if not exists doctor_consulted_today boolean;
alter table public.daily_user_memory_logs add column if not exists doctor_visit boolean;
alter table public.daily_user_memory_logs add column if not exists medical_visit_reason text;
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
