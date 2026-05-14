-- VitaSense setup-context enum repair for older Supabase projects.
-- Run after the data upgrade if onboarding/setup-context save reports enum value errors.

alter type public.recovery_preference_enum add value if not exists 'Rest';
alter type public.recovery_preference_enum add value if not exists 'Talking to Someone';
alter type public.recovery_preference_enum add value if not exists 'Isolation';
alter type public.recovery_preference_enum add value if not exists 'Exercise';
alter type public.recovery_preference_enum add value if not exists 'Entertainment';
alter type public.recovery_preference_enum add value if not exists 'Sleep';
alter type public.recovery_preference_enum add value if not exists 'Food';
alter type public.recovery_preference_enum add value if not exists 'Nature/Travel';

alter type public.stress_response_pattern_enum add value if not exists 'Sleep';
alter type public.stress_response_pattern_enum add value if not exists 'Appetite';
alter type public.stress_response_pattern_enum add value if not exists 'Energy Levels';
alter type public.stress_response_pattern_enum add value if not exists 'Mood';
alter type public.stress_response_pattern_enum add value if not exists 'Focus';
alter type public.stress_response_pattern_enum add value if not exists 'Physical Symptoms';
alter type public.stress_response_pattern_enum add value if not exists 'Everything';

alter type public.life_phase_enum add value if not exists 'Student Life';
alter type public.life_phase_enum add value if not exists 'Early Career';
alter type public.life_phase_enum add value if not exists 'High-Pressure Work Life';
alter type public.life_phase_enum add value if not exists 'Transition Phase';
alter type public.life_phase_enum add value if not exists 'Family-Focused Life';
alter type public.life_phase_enum add value if not exists 'Irregular Lifestyle';

alter type public.social_environment_enum add value if not exists 'Family';
alter type public.social_environment_enum add value if not exists 'Friends/Roommates';
alter type public.social_environment_enum add value if not exists 'Mostly Alone';
alter type public.social_environment_enum add value if not exists 'Hostel Community';
alter type public.social_environment_enum add value if not exists 'Coworkers/Classmates';
alter type public.social_environment_enum add value if not exists 'Mixed';

alter type public.life_structure_type_enum add value if not exists 'Highly Structured';
alter type public.life_structure_type_enum add value if not exists 'Moderately Structured';
alter type public.life_structure_type_enum add value if not exists 'Unpredictable';
alter type public.life_structure_type_enum add value if not exists 'Chaotic';

alter type public.lifestyle_identity_enum add value if not exists 'Health Conscious';
alter type public.lifestyle_identity_enum add value if not exists 'Balanced';
alter type public.lifestyle_identity_enum add value if not exists 'Stress-Driven';
alter type public.lifestyle_identity_enum add value if not exists 'Highly Busy';
alter type public.lifestyle_identity_enum add value if not exists 'Physically Active';
alter type public.lifestyle_identity_enum add value if not exists 'Mentally Exhausted';
alter type public.lifestyle_identity_enum add value if not exists 'Irregular Lifestyle';

alter type public.preferred_environment_enum add value if not exists 'Cold Climate';
alter type public.preferred_environment_enum add value if not exists 'Warm Climate';
alter type public.preferred_environment_enum add value if not exists 'Dry Climate';
alter type public.preferred_environment_enum add value if not exists 'Nature/Outdoors';
alter type public.preferred_environment_enum add value if not exists 'Indoor Controlled Environment';
alter type public.preferred_environment_enum add value if not exists 'No Specific Preference';
