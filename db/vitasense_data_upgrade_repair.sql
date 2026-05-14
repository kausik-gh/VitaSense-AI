-- VitaSense upgrade repair for partially-existing Supabase enum/type definitions.
-- Run after db/vitasense_data_upgrade.sql if live API validation reports enum/type mismatches.

alter type public.body_awareness_level_enum add value if not exists 'Very Aware';
alter type public.body_awareness_level_enum add value if not exists 'Aware';
alter type public.body_awareness_level_enum add value if not exists 'Moderate';
alter type public.body_awareness_level_enum add value if not exists 'Low Awareness';

alter type public.eating_behavior_enum add value if not exists 'Disciplined';
alter type public.eating_behavior_enum add value if not exists 'Emotional Eating';
alter type public.eating_behavior_enum add value if not exists 'Irregular Eating';
alter type public.eating_behavior_enum add value if not exists 'Convenience-Based';
alter type public.eating_behavior_enum add value if not exists 'Late-Night Eating';
alter type public.eating_behavior_enum add value if not exists 'Stress-Based Eating';

alter type public.energy_level_enum add value if not exists 'Very Low';
alter type public.energy_level_enum add value if not exists 'Low';
alter type public.energy_level_enum add value if not exists 'Moderate';
alter type public.energy_level_enum add value if not exists 'Good';
alter type public.energy_level_enum add value if not exists 'High';

alter type public.mood_today_enum add value if not exists 'Very Sad';
alter type public.mood_today_enum add value if not exists 'Sad';
alter type public.mood_today_enum add value if not exists 'Neutral';
alter type public.mood_today_enum add value if not exists 'Happy';
alter type public.mood_today_enum add value if not exists 'Very Happy';
alter type public.mood_today_enum add value if not exists 'Anxious';
alter type public.mood_today_enum add value if not exists 'Stressed';
alter type public.mood_today_enum add value if not exists 'Exhausted';

alter type public.workload_intensity_enum add value if not exists 'Very Low';
alter type public.workload_intensity_enum add value if not exists 'Low';
alter type public.workload_intensity_enum add value if not exists 'Moderate';
alter type public.workload_intensity_enum add value if not exists 'High';
alter type public.workload_intensity_enum add value if not exists 'Extreme';

alter type public.chatbot_risk_level_enum add value if not exists 'Low';
alter type public.chatbot_risk_level_enum add value if not exists 'Medium';
alter type public.chatbot_risk_level_enum add value if not exists 'High';
alter type public.chatbot_risk_level_enum add value if not exists 'Critical';

alter table public.daily_environment_data
  alter column outdoor_hours type numeric
  using outdoor_hours::numeric;

alter table public.daily_fitness_data
  alter column calories_burned type integer
  using round(calories_burned)::integer;

alter table public.daily_fitness_data
  alter column heart_rate_avg type integer
  using round(heart_rate_avg)::integer;
