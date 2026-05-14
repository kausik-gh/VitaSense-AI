import { useEffect, useMemo, useState } from 'react';
import { motion } from 'motion/react';
import {
  Activity,
  ArrowRight,
  BatteryMedium,
  CloudSun,
  Droplets,
  Leaf,
  Moon,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  SunMedium,
  Waves,
  Wind,
} from 'lucide-react';
import { demoWellnessForecast, DEMO_USER_ID } from '../lib/demoData';
import { fetchWellnessForecast, type AlertSeverity, type WellnessForecast, type WellnessMetric } from '../lib/api';

interface WellnessForecastHeroProps {
  userId?: number;
}

const severityStyles: Record<AlertSeverity, string> = {
  low: 'border-[#78a7c8]/30 bg-[#e9f4fb] text-[#164c6a]',
  medium: 'border-[#f5b36b]/35 bg-[#fff3df] text-[#7a4312]',
  high: 'border-error/25 bg-error-container/70 text-on-error-container',
};

const trendCopy = {
  below_baseline: 'Below baseline',
  near_baseline: 'Near baseline',
  above_baseline: 'Above baseline',
  unknown: 'Learning baseline',
};

function formatMetric(metric?: WellnessMetric) {
  if (!metric || metric.value === null) return 'Learning';
  const value = metric.unit === 'ml' ? Math.round(metric.value).toLocaleString() : metric.value.toLocaleString();
  return `${value}${metric.unit === 'steps' ? '' : metric.unit}`;
}

function alertIcon(type: string) {
  if (type === 'air_quality') return Wind;
  if (type === 'pollen') return Leaf;
  if (type === 'uv') return SunMedium;
  return CloudSun;
}

export function WellnessForecastHero({ userId = DEMO_USER_ID }: WellnessForecastHeroProps) {
  const [forecast, setForecast] = useState<WellnessForecast>(demoWellnessForecast);
  const [status, setStatus] = useState<'loading' | 'live' | 'fallback'>('loading');

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');

    fetchWellnessForecast(userId, controller.signal)
      .then((nextForecast) => {
        setForecast(nextForecast);
        setStatus('live');
      })
      .catch(() => {
        setForecast(demoWellnessForecast);
        setStatus('fallback');
      });

    return () => controller.abort();
  }, [userId]);

  const topMetrics = useMemo(
    () => [
      { key: 'sleep', icon: Moon, label: 'Sleep', value: formatMetric(forecast.metrics.sleep), trend: forecast.metrics.sleep?.trend ?? 'unknown' },
      { key: 'hydration', icon: Droplets, label: 'Hydration', value: formatMetric(forecast.metrics.hydration), trend: forecast.metrics.hydration?.trend ?? 'unknown' },
      { key: 'hrv', icon: Waves, label: 'Recovery', value: formatMetric(forecast.metrics.hrv), trend: forecast.metrics.hrv?.trend ?? 'unknown' },
    ],
    [forecast.metrics],
  );

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: 'easeOut' }}
      className="relative overflow-hidden rounded-[2rem] bg-[#101715] text-white shadow-2xl shadow-black/15"
    >
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#94d4bb] via-[#78a7c8] to-[#ffb4a4]" />
      <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="relative p-6 sm:p-8 lg:p-10">
          <div className="flex flex-wrap items-center gap-3 mb-8">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-1.5 text-[11px] font-bold uppercase tracking-widest text-[#aff0d6]">
              <Sparkles className="h-3.5 w-3.5" />
              Wellness Forecast
            </span>
            <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/6 px-3 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/65">
              {status === 'live' ? 'Live intelligence' : status === 'loading' ? 'Syncing signals' : 'Demo forecast'}
              {status === 'loading' && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
            </span>
          </div>

          <div className="max-w-3xl">
            <p className="mb-3 text-sm font-bold uppercase tracking-widest text-[#94d4bb]/80">Good morning, Samantha</p>
            <h2 className="text-4xl font-black leading-[1.02] tracking-normal sm:text-5xl lg:text-6xl">
              {forecast.headline}
            </h2>
            <p className="mt-6 max-w-2xl text-base font-medium leading-8 text-white/72 sm:text-lg">
              {forecast.summary}
            </p>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {topMetrics.map((metric) => (
              <motion.div
                key={metric.key}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl border border-white/10 bg-white/[0.07] p-4"
              >
                <div className="mb-4 flex items-center justify-between">
                  <metric.icon className="h-5 w-5 text-[#94d4bb]" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-white/45">{trendCopy[metric.trend]}</span>
                </div>
                <p className="text-xs font-bold uppercase tracking-widest text-white/45">{metric.label}</p>
                <p className="mt-1 text-2xl font-black">{metric.value}</p>
              </motion.div>
            ))}
          </div>
        </div>

        <aside className="border-t border-white/10 bg-white/[0.04] p-6 sm:p-8 xl:border-l xl:border-t-0">
          <div className="grid grid-cols-[auto_1fr] items-center gap-5 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <div className="relative h-28 w-28">
              <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.10)" strokeWidth="12" />
                <motion.circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#94d4bb"
                  strokeLinecap="round"
                  strokeWidth="12"
                  strokeDasharray="314"
                  initial={{ strokeDashoffset: 314 }}
                  animate={{ strokeDashoffset: 314 - (forecast.readiness_score / 100) * 314 }}
                  transition={{ duration: 0.9, ease: 'easeOut' }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-black">{forecast.readiness_score}</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-white/45">Ready</span>
              </div>
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-white/45">Predicted State</p>
              <p className="mt-2 text-2xl font-black capitalize">{forecast.energy.state}</p>
              <p className="mt-2 text-sm font-medium leading-6 text-white/58">
                Energy {forecast.energy.score}% · Recovery {forecast.recovery.score}%
              </p>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-3">
            {forecast.patterns.slice(0, 2).map((pattern, index) => (
              <motion.div
                key={pattern.title}
                initial={{ opacity: 0, x: 14 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.12 + index * 0.06 }}
                className="rounded-2xl border border-white/10 bg-white/[0.06] p-4"
              >
                <div className="flex items-center gap-3">
                  <BatteryMedium className="h-5 w-5 text-[#ffb4a4]" />
                  <p className="text-sm font-black">{pattern.title}</p>
                </div>
                <p className="mt-2 text-sm font-medium leading-6 text-white/58">{pattern.detail}</p>
              </motion.div>
            ))}
          </div>

          <div className="mt-5 space-y-3">
            {forecast.environmental_alerts.slice(0, 2).map((alert) => {
              const Icon = alertIcon(alert.type);
              return (
                <div key={`${alert.type}-${alert.title}`} className={`rounded-2xl border p-4 ${severityStyles[alert.severity]}`}>
                  <div className="flex items-start gap-3">
                    <Icon className="mt-0.5 h-5 w-5 shrink-0" />
                    <div>
                      <p className="text-sm font-black">{alert.title}</p>
                      <p className="mt-1 text-xs font-semibold leading-5 opacity-75">{alert.detail}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>
      </div>

      <div className="border-t border-white/10 px-6 py-5 sm:px-8 lg:px-10">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-3">
            {forecast.suggested_actions.slice(0, 3).map((action) => (
              <div key={action.title} className="rounded-full border border-white/10 bg-white/[0.07] px-4 py-2 text-xs font-bold text-white/72">
                {action.title}
              </div>
            ))}
          </div>
          <button className="inline-flex items-center justify-center gap-2 rounded-full bg-[#aff0d6] px-5 py-3 text-sm font-black text-[#002117] transition-transform hover:scale-[1.02] active:scale-[0.98]">
            Review today’s plan
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-4 flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-white/35">
          <ShieldCheck className="h-4 w-4" />
          Built from your recent sleep, recovery, environment, behavior, and profile signals
        </div>
      </div>
    </motion.section>
  );
}
