import { motion } from 'motion/react';
import { AlertTriangle, Brain, ShieldAlert, Utensils } from 'lucide-react';
import { AreaHealthIntelligenceMap } from '../components/AreaHealthIntelligenceMap';

const predictiveCards = [
  {
    title: 'Viral exposure risk',
    value: 'High',
    detail: 'Local fever activity, crowded exposure, and weather volatility are aligned today.',
    icon: ShieldAlert,
  },
  {
    title: 'Respiratory irritation',
    value: 'Medium',
    detail: 'AQI and throat-irritation reports are both elevated in the nearby cluster.',
    icon: AlertTriangle,
  },
  {
    title: 'Food safety caution',
    value: 'Medium',
    detail: 'Street-food complaints and stomach-infection reports are concentrated west of your area.',
    icon: Utensils,
  },
  {
    title: 'Burnout probability',
    value: 'Watch',
    detail: 'Sleep, workload, screen load, and local stress reports suggest a lighter evening.',
    icon: Brain,
  },
];

export function AreaHealthMapScreen() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      <section>
        <p className="mb-2 text-xs font-black uppercase text-primary">Community intelligence</p>
        <h1 className="text-4xl font-black text-on-background">Area Health Map</h1>
        <p className="mt-2 max-w-3xl text-sm font-semibold text-on-surface-variant opacity-70">
          Local disease signals, community symptoms, hazards, food safety, and lifestyle risk in one locality view.
        </p>
      </section>

      <AreaHealthIntelligenceMap />

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {predictiveCards.map((card) => (
          <div key={card.title} className="rounded-[2rem] border border-outline-variant/25 bg-white p-6 shadow-xl shadow-black/5">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <card.icon className="h-6 w-6" />
              </div>
              <span className="rounded-full bg-surface-container px-3 py-1 text-[10px] font-black uppercase text-on-surface-variant">
                {card.value}
              </span>
            </div>
            <h3 className="text-lg font-black text-on-surface">{card.title}</h3>
            <p className="mt-3 text-sm font-semibold leading-relaxed text-on-surface-variant opacity-75">{card.detail}</p>
          </div>
        ))}
      </section>
    </motion.div>
  );
}
