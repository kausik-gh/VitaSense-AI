import type { WellnessForecast } from './api';

export const DEMO_USER_ID = Number(import.meta.env.VITE_DEMO_USER_ID ?? 1);

export const demoWellnessForecast: WellnessForecast = {
  user_id: DEMO_USER_ID,
  date: '2026-05-14',
  headline: 'Today may need a gentler rhythm with 58% readiness.',
  summary:
    'Good morning. Based on lighter sleep, hydration running below your recent baseline, and elevated air quality pressure, your energy may feel uneven today. Front-load hydration and keep the afternoon lighter if your schedule allows it.',
  readiness_score: 58,
  energy: {
    score: 52,
    state: 'delicate',
    trend: 'below_baseline',
  },
  recovery: {
    score: 64,
    state: 'watchful',
    trend: 'below_baseline',
  },
  patterns: [
    {
      title: 'Sleep pressure',
      detail: 'Sleep is running light today, which may lower morning energy and stress tolerance.',
    },
    {
      title: 'Hydration drift',
      detail: 'Water intake appears below a supportive range, so fatigue or headache risk may be higher.',
    },
    {
      title: 'Workload compression',
      detail: 'Today looks cognitively demanding, so recovery breaks may matter more than usual.',
    },
  ],
  suggested_actions: [
    {
      title: 'Front-load hydration',
      detail: 'Add water earlier in the day rather than waiting until evening.',
    },
    {
      title: 'Keep the afternoon lighter',
      detail: 'A lighter afternoon workload may help protect energy if your schedule allows it.',
    },
    {
      title: 'Reduce outdoor exposure',
      detail: 'Poor air quality may make indoor or low-exertion plans more supportive today.',
    },
  ],
  environmental_alerts: [
    {
      type: 'air_quality',
      severity: 'medium',
      title: 'AQI sensitivity watch',
      detail: 'Air quality is elevated and may be more relevant because of your respiratory or throat history.',
    },
    {
      type: 'pollen',
      severity: 'medium',
      title: 'Allergy load',
      detail: 'Pollen may be more noticeable today based on your allergy context.',
    },
  ],
  metrics: {
    sleep: {
      label: 'Sleep',
      value: 5.5,
      baseline: 7.1,
      unit: 'h',
      trend: 'below_baseline',
    },
    hydration: {
      label: 'Hydration',
      value: 1100,
      baseline: 2200,
      unit: 'ml',
      trend: 'below_baseline',
    },
    hrv: {
      label: 'Recovery',
      value: 35,
      baseline: 49,
      unit: 'ms',
      trend: 'below_baseline',
    },
  },
  source_tables: ['daily_fitness_data', 'daily_environment_data', 'user_medical_identity'],
};
