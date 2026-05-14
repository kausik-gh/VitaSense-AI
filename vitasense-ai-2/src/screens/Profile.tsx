import { motion } from 'motion/react';
import { 
  Users, 
  Utensils, 
  Stethoscope, 
  FileText, 
  X, 
  ShieldCheck, 
  FileCheck,
  Edit2,
  Clock,
  HeartPulse,
  Activity
} from 'lucide-react';

export function ProfileScreen() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-10"
    >
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl font-extrabold text-on-surface tracking-tight">Health Profile</h1>
          <p className="text-lg font-medium text-on-surface-variant opacity-70">Review and manage your core clinical and lifestyle data.</p>
        </div>
        <button className="bg-primary text-white px-8 py-4 rounded-2xl font-bold flex items-center gap-3 hover:opacity-90 shadow-xl shadow-primary/20 transition-all active:scale-[0.98]">
          <Edit2 className="w-5 h-5" />
          Edit Profile
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        <section className="md:col-span-8 bg-white p-10 rounded-[2.5rem] shadow-xl shadow-black/5 border border-white">
          <div className="flex items-center gap-4 mb-10">
            <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold">Life Context</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-10 gap-x-8">
            <div className="space-y-2">
              <span className="text-xs font-black text-on-surface-variant uppercase tracking-widest opacity-40">Marital Status</span>
              <p className="text-lg font-semibold">Married, 2 Children</p>
            </div>
            <div className="space-y-2">
              <span className="text-xs font-black text-on-surface-variant uppercase tracking-widest opacity-40">Work Environment</span>
              <p className="text-lg font-semibold">Corporate Office, 8h Sitting</p>
            </div>
          </div>
        </section>

        <section className="md:col-span-4 bg-[#7ab9a1]/10 p-10 rounded-[2.5rem] border border-[#7ab9a1]/20">
          <div className="flex items-center gap-4 mb-10">
            <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center text-primary">
              <Utensils className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold">Food & Body</h3>
          </div>
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-2xl flex items-center justify-between shadow-sm">
              <span className="text-sm font-bold opacity-70">Current BMI</span>
              <span className="text-2xl font-black text-primary">22.4</span>
            </div>
          </div>
        </section>

        <section className="md:col-span-4 bg-zinc-900 p-10 rounded-[2.5rem] text-white shadow-2xl overflow-hidden relative">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/20 rounded-full blur-3xl"></div>
          <div className="flex items-center gap-4 mb-10 relative z-10">
            <div className="w-12 h-12 rounded-2xl bg-primary/30 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold">Daily Routine</h3>
          </div>
          <ul className="space-y-6 relative z-10">
            {['07:00 朝 (Morning Yoga)', '12:30 (Lunch)', '22:00 (Wind-down)'].map((task, i) => (
              <li key={i} className="flex items-center gap-4 border-l-2 border-primary/20 pl-4 py-1">
                <span className="text-[10px] font-black opacity-40 uppercase tracking-widest">{task.split(' ')[0]}</span>
                <span className="text-sm font-semibold">{task.split(' ').slice(1).join(' ')}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="md:col-span-8 bg-white p-10 rounded-[2.5rem] shadow-xl shadow-black/5 border border-white">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-tertiary-container/20 flex items-center justify-center text-tertiary">
                <Stethoscope className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-bold">Medical Snapshots</h3>
            </div>
            <span className="text-[10px] font-black text-tertiary bg-tertiary-container/10 px-4 py-1 rounded-full uppercase tracking-widest">High Precision</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
            {[
              { label: 'Blood Group', value: 'O Positive' },
              { label: 'Avg Blood Pressure', value: '118/76 mmHg' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col gap-2 border-b border-surface-container pb-4">
                <span className="text-xs font-black text-on-surface-variant uppercase tracking-widest opacity-40">{item.label}</span>
                <span className="text-lg font-bold">{item.value}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="md:col-span-12">
          <div className="bg-secondary-container/10 border-4 border-dashed border-secondary-container/50 p-10 rounded-[2.5rem] flex flex-col md:flex-row items-center justify-between gap-10">
            <div className="max-w-md">
              <h3 className="text-3xl font-black text-secondary mb-3">Health Record Imports</h3>
              <p className="text-base font-medium text-on-surface-variant opacity-70">
                Keep your AI companion updated by uploading latest medical documentation.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {[
                { label: 'Blood Reports', icon: Activity },
                { label: 'Prescriptions', icon: FileText },
                { label: 'BP Reports', icon: HeartPulse },
              ].map((btn, i) => (
                <button key={i} className="bg-white p-6 rounded-3xl border-2 border-transparent hover:border-primary transition-all flex flex-col items-center gap-3">
                  <btn.icon className="w-10 h-10 text-primary" />
                  <span className="text-sm font-bold">{btn.label}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>

      <footer className="pt-12 text-center opacity-50 flex flex-col items-center gap-4">
        <div className="w-16 h-16 bg-surface-container rounded-full flex items-center justify-center text-primary/60">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <p className="text-xs font-black uppercase tracking-widest">Encrypted Clinical Data Vault</p>
      </footer>
    </motion.div>
  );
}
