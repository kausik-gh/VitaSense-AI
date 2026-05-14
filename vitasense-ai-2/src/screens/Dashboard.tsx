import { motion } from 'motion/react';
import { Heart, Moon, ChevronRight, MoreHorizontal, ChevronLeft, Brain } from 'lucide-react';
import { WellnessForecastHero } from '../components/WellnessForecastHero';
import { AreaHealthIntelligenceMap } from '../components/AreaHealthIntelligenceMap';

interface DashboardScreenProps {
  onAction: (action: string) => void;
}

export function DashboardScreen({ onAction }: DashboardScreenProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      {/* Greeting Area */}
      <section>
        <h2 className="text-3xl font-black tracking-tight text-on-background sm:text-4xl">Good morning, Samantha</h2>
        <p className="mt-1 text-sm font-black uppercase tracking-wide text-primary/75 sm:text-base">Thursday, 14 May 2026</p>
      </section>

      <WellnessForecastHero />

      <AreaHealthIntelligenceMap compact />

      {/* Main Layout Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Content (8 cols) */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Onboarding Call to Action */}
          <div className="premium-panel premium-interactive relative overflow-hidden rounded-[2rem] p-8">
            <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
              <div className="flex-1 text-center md:text-left">
                <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1 text-xs font-black text-primary">Action Required</span>
                <h3 className="text-2xl font-bold text-on-background mb-4 leading-tight">Complete your profile to sharpen tomorrow’s forecast</h3>
                <p className="text-on-surface-variant font-medium mb-8 max-w-md mx-auto md:mx-0 opacity-80">
                  VitaSense can personalize predictions more precisely when your lifestyle, allergy, and recovery context are up to date.
                </p>
                <button 
                  onClick={() => onAction('onboarding')}
                  className="rounded-full bg-primary px-7 py-3 text-sm font-black text-white shadow-xl shadow-primary/20 transition-all duration-200 hover:bg-[#08513e] hover:shadow-2xl hover:shadow-primary/25 active:scale-[0.98]"
                >
                  Update Profile
                </button>
              </div>
              <div className="w-full md:w-1/3">
                <div className="bg-surface-container rounded-2xl p-3 ring-8 ring-white/50">
                  <img 
                    alt="Health Dashboard" 
                    loading="lazy"
                    className="w-full h-auto rounded-xl" 
                    src="https://images.unsplash.com/photo-1551288049-bbda38a10ad5?w=400&auto=format&fit=crop&q=80" 
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Secondary Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            <div className="premium-panel premium-interactive flex items-center gap-6 rounded-[2rem] p-8">
              <div className="w-14 h-14 bg-[#aff0d6]/30 rounded-2xl flex items-center justify-center text-primary">
                <Heart className="w-8 h-8 fill-primary" />
              </div>
              <div>
                <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest opacity-60">Heart Rate</p>
                <p className="text-2xl font-bold text-on-background">-- bpm</p>
              </div>
            </div>
            <div className="premium-panel premium-interactive flex items-center gap-6 rounded-[2rem] p-8">
              <div className="w-14 h-14 bg-secondary-container/30 rounded-2xl flex items-center justify-center text-secondary">
                <Moon className="w-8 h-8 fill-secondary" />
              </div>
              <div>
                <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest opacity-60">Sleep Quality</p>
                <p className="text-2xl font-bold text-on-background">-- %</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Content (4 cols) */}
        <aside className="lg:col-span-4 space-y-8">
          <div className="premium-panel rounded-[2rem] p-8">
            <div className="flex justify-between items-center mb-6">
              <h4 className="text-xl font-bold text-on-background">Upcoming Appointments</h4>
              <MoreHorizontal className="w-5 h-5 text-on-surface-variant cursor-pointer" />
            </div>

            <div className="flex border-b border-surface-container mb-8">
              <button className="flex-1 py-3 text-sm font-bold text-primary border-b-2 border-primary transition-all">Monthly</button>
              <button className="flex-1 py-3 text-sm font-medium text-on-surface-variant opacity-60 hover:opacity-100 transition-all">Daily</button>
            </div>

            {/* Calendar Mock */}
            <div className="mb-10">
              <div className="flex justify-between items-center px-2 mb-6">
                <span className="text-sm font-black">May 2026</span>
                <div className="flex gap-4">
                  <ChevronLeft className="h-4 w-4 cursor-pointer transition-colors hover:text-primary" />
                  <ChevronRight className="h-4 w-4 cursor-pointer transition-colors hover:text-primary" />
                </div>
              </div>
              <div className="grid grid-cols-7 gap-2 text-center text-[10px] font-bold opacity-30 uppercase tracking-tighter mb-4">
                <span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span>
              </div>
              <div className="grid grid-cols-7 gap-2 text-center">
                {[11, 12, 13].map(d => (
                  <div key={d} className="h-10 flex items-center justify-center text-xs font-medium text-on-surface-variant opacity-50">{d}</div>
                ))}
                <div className="h-10 flex items-center justify-center text-xs font-black bg-primary text-white rounded-full shadow-lg shadow-primary/30">14</div>
                {[15, 16, 17].map(d => (
                  <div key={d} className="h-10 flex items-center justify-center text-xs font-medium text-on-surface-variant opacity-50">{d}</div>
                ))}
              </div>
            </div>

            {/* List */}
            <div className="space-y-4">
              <div className="group flex cursor-pointer items-center gap-4 rounded-2xl border border-surface-container bg-surface p-4 transition-all duration-200 hover:border-primary-container hover:bg-primary/5">
                <div className="w-12 h-12 bg-secondary-fixed rounded-full flex items-center justify-center text-secondary">
                  <Brain className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold group-hover:text-primary transition-colors">Manage stress</p>
                  <p className="text-[10px] font-medium text-on-surface-variant opacity-60">10:00pm - 12:00pm</p>
                </div>
                <ChevronRight className="w-4 h-4 text-on-surface-variant" />
              </div>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-[2.5rem] bg-on-background p-8 shadow-2xl shadow-black/15">
            <div className="relative z-10 text-white">
              <h4 className="text-xl font-bold mb-2">Daily progress</h4>
              <p className="text-xs text-surface-variant opacity-70 mb-8 font-medium">Keep improving the quality of your health</p>
              
              <div className="flex items-center justify-center py-4">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle className="text-white/10" cx="80" cy="80" fill="transparent" r="72" stroke="currentColor" strokeWidth="12"></circle>
                    <circle className="text-primary-container" cx="80" cy="80" fill="transparent" r="72" stroke="currentColor" strokeDasharray="452" strokeDashoffset="90" strokeWidth="12" strokeLinecap="round"></circle>
                  </svg>
                  <span className="absolute text-4xl font-black">80%</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </motion.div>
  );
}
