import { motion } from 'motion/react';
import { VitalSignsIcon, HealthSafetyIcon, ShieldCheckIcon } from '../components/Icons';

interface WelcomeScreenProps {
  onStart: (type: 'new' | 'old') => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-tr from-[#aff0d6]/30 via-[#fbf9f8] to-[#fbf9f8]">
      <motion.main 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-xl glass-card p-12 rounded-[2.5rem] shadow-2xl text-center relative overflow-hidden"
      >
        <div className="mb-10 flex flex-col items-center">
          <div className="w-20 h-20 bg-primary-container rounded-3xl flex items-center justify-center mb-6 shadow-lg shadow-primary-container/20">
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
              className="w-full h-full object-cover transition-transform duration-700 hover:scale-105" 
              src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&auto=format&fit=crop&q=80"
            />
          </div>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row items-center justify-center w-full">
          <button 
            onClick={() => onStart('new')}
            className="w-full sm:w-1/2 h-14 bg-primary hover:bg-[#08513e] text-white font-bold rounded-full shadow-lg transition-all active:scale-[0.98]"
          >
            New User
          </button>
          <button 
            onClick={() => onStart('old')}
            className="w-full sm:w-1/2 h-14 border-2 border-primary-container bg-transparent text-primary hover:bg-primary-container/10 font-bold rounded-full transition-all active:scale-[0.98]"
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

      <div className="absolute top-[15%] left-[10%] bg-white/80 backdrop-blur-md p-3 rounded-2xl shadow-xl border border-primary/10 flex items-center gap-3 hidden lg:flex">
        <VitalSignsIcon className="text-primary w-5 h-5" />
        <span className="text-primary font-bold text-xs uppercase tracking-wider">Vital Stats: Optimal</span>
      </div>
      
      <div className="absolute bottom-[20%] right-[10%] bg-white/80 backdrop-blur-md p-3 rounded-2xl shadow-xl border border-primary/10 flex items-center gap-3 hidden lg:flex">
        <ShieldCheckIcon className="text-secondary w-5 h-5" />
        <span className="text-secondary font-bold text-xs uppercase tracking-wider">AI Secure Analysis</span>
      </div>
    </div>
  );
}

