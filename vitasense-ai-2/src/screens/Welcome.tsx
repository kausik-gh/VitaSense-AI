import { motion } from 'motion/react';
import { VitalSignsIcon, HealthSafetyIcon, ShieldCheckIcon } from '../components/Icons';

interface WelcomeScreenProps {
  onStart: (type: 'new' | 'old') => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[linear-gradient(135deg,#f4faf7_0%,#fbf9f8_48%,#eef8fb_100%)]">
      <motion.main 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
        className="relative w-full max-w-xl overflow-hidden rounded-[2.5rem] p-8 text-center shadow-2xl shadow-black/10 sm:p-12 glass-card"
      >
        <div className="mb-10 flex flex-col items-center">
          <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-primary-container shadow-lg shadow-primary-container/20 ring-8 ring-primary-container/10">
            <VitalSignsIcon className="text-white w-12 h-12" />
          </div>
          <h1 className="text-primary font-bold text-4xl mb-2 tracking-tight">VitaSense AI</h1>
          <p className="text-on-surface-variant font-medium text-lg max-w-xs mx-auto opacity-70">
            Your personalized preventive healthcare companion
          </p>
        </div>

        <div className="mb-10 px-4">
          <div className="aspect-video w-full rounded-2xl overflow-hidden bg-surface-container-low shadow-inner">
            <img 
              alt="Healthcare Professional" 
              loading="lazy"
              className="h-full w-full object-cover transition-transform duration-700 hover:scale-105" 
              src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&auto=format&fit=crop&q=80"
            />
          </div>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row items-center justify-center w-full">
          <button 
            onClick={() => onStart('new')}
            className="h-14 w-full rounded-full bg-primary font-bold text-white shadow-lg shadow-primary/20 transition-all duration-200 hover:bg-[#08513e] hover:shadow-xl hover:shadow-primary/25 active:scale-[0.98] sm:w-1/2"
          >
            New User
          </button>
          <button 
            onClick={() => onStart('old')}
            className="h-14 w-full rounded-full border-2 border-primary-container bg-white/70 font-bold text-primary transition-all duration-200 hover:border-primary hover:bg-primary-container/15 active:scale-[0.98] sm:w-1/2"
          >
            Old User
          </button>
        </div>

        <div className="mt-10 pt-6 border-t border-outline-variant/30">
          <p className="text-on-surface-variant font-medium text-xs opacity-60">
            Empowering your journey to peak health through intelligent insights.
          </p>
        </div>

        {/* Decorative elements */}
        <div className="absolute -bottom-10 -left-10 opacity-5 pointer-events-none">
          <HealthSafetyIcon className="text-primary w-48 h-48" />
        </div>
      </motion.main>

      <div className="absolute left-[10%] top-[15%] hidden items-center gap-3 rounded-2xl border border-primary/10 bg-white/85 p-3 shadow-xl shadow-black/5 backdrop-blur-md lg:flex">
        <VitalSignsIcon className="text-primary w-5 h-5" />
        <span className="text-primary font-bold text-xs uppercase tracking-wider">Vital Stats: Optimal</span>
      </div>
      
      <div className="absolute bottom-[20%] right-[10%] hidden items-center gap-3 rounded-2xl border border-primary/10 bg-white/85 p-3 shadow-xl shadow-black/5 backdrop-blur-md lg:flex">
        <ShieldCheckIcon className="text-secondary w-5 h-5" />
        <span className="text-secondary font-bold text-xs uppercase tracking-wider">AI Secure Analysis</span>
      </div>
    </div>
  );
}
