import {
  Activity,
  AlertTriangle,
  CloudSun,
  Droplets,
  Flame,
  Map,
  Radar,
  ShieldAlert,
  ThermometerSun,
  Utensils,
  Users,
  Wind,
} from 'lucide-react';
import { motion } from 'motion/react';
import { useMemo, useState } from 'react';

type IntelligenceLayer = 'disease' | 'symptoms' | 'hazards' | 'food' | 'predictive';
type Severity = 'low' | 'medium' | 'high';

type Hotspot = {
  id: string;
  layer: IntelligenceLayer;
  title: string;
  detail: string;
  severity: Severity;
  distance: string;
  x: number;
  y: number;
  icon: typeof Activity;
};

const layerMeta: Record<IntelligenceLayer, { label: string; icon: typeof Activity; tone: string }> = {
  disease: { label: 'Disease', icon: ShieldAlert, tone: 'bg-rose-500' },
  symptoms: { label: 'Symptoms', icon: Users, tone: 'bg-sky-500' },
  hazards: { label: 'Hazards', icon: CloudSun, tone: 'bg-amber-500' },
  food: { label: 'Food Safety', icon: Utensils, tone: 'bg-violet-500' },
  predictive: { label: 'Predictive', icon: Radar, tone: 'bg-primary' },
};

const hotspots: Hotspot[] = [
  {
    id: 'viral-fever',
    layer: 'disease',
    title: 'Viral fever activity',
    detail: 'High viral fever activity detected within 3km of your area.',
    severity: 'high',
    distance: '2.7 km',
    x: 63,
    y: 34,
    icon: ShieldAlert,
  },
  {
    id: 'dengue-watch',
    layer: 'disease',
    title: 'Dengue watch zone',
    detail: 'Mosquito growth conditions are elevated after stagnant-water reports.',
    severity: 'medium',
    distance: '1.8 km',
    x: 31,
    y: 58,
    icon: Droplets,
  },
  {
    id: 'throat-cluster',
    layer: 'symptoms',
    title: 'Throat irritation cluster',
    detail: '12 nearby users reported throat irritation in the last 48 hours.',
    severity: 'medium',
    distance: '1.2 km',
    x: 48,
    y: 42,
    icon: Users,
  },
  {
    id: 'cough-outbreak',
    layer: 'symptoms',
    title: 'Cough reports rising',
    detail: 'Cough and fatigue reports are trending above the local baseline.',
    severity: 'low',
    distance: '3.4 km',
    x: 76,
    y: 63,
    icon: Activity,
  },
  {
    id: 'drainage-overflow',
    layer: 'hazards',
    title: 'Drainage overflow',
    detail: 'Drainage overflow reported near your locality. Mosquito-borne risk may rise.',
    severity: 'high',
    distance: '0.9 km',
    x: 39,
    y: 72,
    icon: AlertTriangle,
  },
  {
    id: 'pollution-spike',
    layer: 'hazards',
    title: 'Pollution spike',
    detail: 'AQI spike may correlate with cough, fatigue, and allergy irritation today.',
    severity: 'medium',
    distance: '2.1 km',
    x: 68,
    y: 52,
    icon: Wind,
  },
  {
    id: 'food-cluster',
    layer: 'food',
    title: 'Street-food caution',
    detail: 'Several stomach infection reports are clustered near a snack vendor corridor.',
    severity: 'high',
    distance: '1.5 km',
    x: 57,
    y: 76,
    icon: Utensils,
  },
  {
    id: 'water-alert',
    layer: 'food',
    title: 'Unsafe water advisory',
    detail: 'Avoid raw street juices locally today due to contamination reports.',
    severity: 'medium',
    distance: '2.9 km',
    x: 24,
    y: 38,
    icon: Droplets,
  },
  {
    id: 'burnout-risk',
    layer: 'predictive',
    title: 'Burnout risk',
    detail: 'Sleep debt, workload, and screen load point to higher fatigue probability.',
    severity: 'medium',
    distance: 'Personal',
    x: 50,
    y: 50,
    icon: Radar,
  },
  {
    id: 'dehydration-risk',
    layer: 'predictive',
    title: 'Dehydration probability',
    detail: 'Heat, outdoor exposure, and recent hydration suggest a watchful day.',
    severity: 'low',
    distance: 'Personal',
    x: 78,
    y: 29,
    icon: ThermometerSun,
  },
];

const severityClass: Record<Severity, string> = {
  low: 'border-sky-200 bg-sky-50 text-sky-800',
  medium: 'border-amber-200 bg-amber-50 text-amber-800',
  high: 'border-rose-200 bg-rose-50 text-rose-800',
};

const pulseClass: Record<Severity, string> = {
  low: 'bg-sky-500 shadow-sky-500/30',
  medium: 'bg-amber-500 shadow-amber-500/30',
  high: 'bg-rose-500 shadow-rose-500/30',
};

interface AreaHealthIntelligenceMapProps {
  compact?: boolean;
}

export function AreaHealthIntelligenceMap({ compact = false }: AreaHealthIntelligenceMapProps) {
  const [activeLayer, setActiveLayer] = useState<IntelligenceLayer>('disease');
  const visibleHotspots = useMemo(
    () => hotspots.filter((hotspot) => hotspot.layer === activeLayer),
    [activeLayer],
  );
  const activeHotspot = visibleHotspots[0] ?? hotspots[0];
  const ActiveIcon = layerMeta[activeLayer].icon;

  return (
    <section className="overflow-hidden rounded-[2rem] bg-zinc-950 text-white shadow-2xl shadow-black/20">
      <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="relative min-h-[430px] border-b border-white/10 p-6 lg:border-b-0 lg:border-r">
          <div className="relative z-10 flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-[11px] font-black uppercase tracking-wide text-[#aff0d6]">
                <Map className="h-4 w-4" />
                Area Health Map
              </div>
              <h2 className={`${compact ? 'text-2xl' : 'text-3xl'} font-black tracking-tight`}>
                Live locality intelligence
              </h2>
              <p className="mt-2 max-w-xl text-sm font-medium text-white/60">
                Koramangala sector scan · 3km radius · refreshed 18 min ago
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">
              <p className="text-[10px] font-black uppercase text-white/45">Overall signal</p>
              <p className="mt-1 text-2xl font-black text-[#aff0d6]">Elevated</p>
            </div>
          </div>

          <div className="relative mt-8 h-[300px] overflow-hidden rounded-[1.75rem] border border-white/10 bg-[#12231f]">
            <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(255,255,255,.12)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.12)_1px,transparent_1px)] [background-size:48px_48px]" />
            <div className="absolute left-[8%] top-[22%] h-[38%] w-[72%] rounded-full border border-[#aff0d6]/25" />
            <div className="absolute left-[18%] top-[14%] h-[58%] w-[52%] rotate-12 rounded-[45%] border border-white/10" />
            <div className="absolute left-0 top-[47%] h-2 w-full rotate-[-10deg] bg-white/8" />
            <div className="absolute left-[38%] top-0 h-full w-2 rotate-[22deg] bg-white/8" />
            <div className="absolute bottom-5 left-5 rounded-full border border-white/10 bg-black/30 px-3 py-2 text-[10px] font-black uppercase text-white/60">
              3km radius
            </div>

            {visibleHotspots.map((hotspot) => {
              const Icon = hotspot.icon;
              return (
                <motion.div
                  key={hotspot.id}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute"
                  style={{ left: `${hotspot.x}%`, top: `${hotspot.y}%` }}
                >
                  <div className={`relative flex h-11 w-11 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full ${pulseClass[hotspot.severity]} shadow-2xl`}>
                    <span className={`absolute h-11 w-11 animate-ping rounded-full ${pulseClass[hotspot.severity]} opacity-30`} />
                    <Icon className="relative h-5 w-5 text-white" />
                  </div>
                </motion.div>
              );
            })}

            <div className="absolute bottom-5 right-5 w-[min(280px,70%)] rounded-2xl border border-white/10 bg-black/55 p-4 backdrop-blur-md">
              <p className="text-[10px] font-black uppercase text-white/45">{activeHotspot.distance}</p>
              <h3 className="mt-1 text-base font-black">{activeHotspot.title}</h3>
              <p className="mt-2 text-xs font-medium leading-relaxed text-white/65">{activeHotspot.detail}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 text-on-surface">
          <div className="grid grid-cols-2 gap-2">
            {(Object.keys(layerMeta) as IntelligenceLayer[]).map((layer) => {
              const meta = layerMeta[layer];
              const Icon = meta.icon;
              const isActive = activeLayer === layer;
              return (
                <button
                  key={layer}
                  type="button"
                  onClick={() => setActiveLayer(layer)}
                  className={`flex items-center gap-2 rounded-2xl border px-3 py-3 text-left text-xs font-black transition-all ${
                    isActive
                      ? 'border-primary bg-primary text-white shadow-lg shadow-primary/20'
                      : 'border-outline-variant/30 bg-surface-container/60 text-on-surface-variant hover:border-primary/40'
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {meta.label}
                </button>
              );
            })}
          </div>

          <div className="mt-6 rounded-[1.5rem] bg-surface-container/70 p-5">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${layerMeta[activeLayer].tone} text-white`}>
                  <ActiveIcon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-[10px] font-black uppercase text-on-surface-variant opacity-50">Active layer</p>
                  <p className="text-base font-black">{layerMeta[activeLayer].label}</p>
                </div>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-[10px] font-black text-primary">
                {visibleHotspots.length} signals
              </span>
            </div>
            <div className="space-y-3">
              {visibleHotspots.map((hotspot) => (
                <div key={hotspot.id} className={`rounded-2xl border p-4 ${severityClass[hotspot.severity]}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-black">{hotspot.title}</p>
                      <p className="mt-1 text-xs font-semibold opacity-75">{hotspot.detail}</p>
                    </div>
                    <span className="rounded-full bg-white/70 px-2 py-1 text-[10px] font-black uppercase">
                      {hotspot.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {!compact && (
            <div className="mt-6 grid grid-cols-2 gap-3">
              {[
                { label: 'Local reports', value: '42', icon: Users },
                { label: 'Food alerts', value: '3', icon: Utensils },
                { label: 'Heat zones', value: '2', icon: Flame },
                { label: 'Pollution score', value: '160', icon: Wind },
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-outline-variant/25 bg-white p-4">
                  <item.icon className="mb-3 h-5 w-5 text-primary" />
                  <p className="text-[10px] font-black uppercase text-on-surface-variant opacity-50">{item.label}</p>
                  <p className="mt-1 text-2xl font-black">{item.value}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
