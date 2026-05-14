import { Bell, Search, ShieldCheck } from 'lucide-react';

interface TopBarProps {
  title?: string;
  userName?: string;
  onNavigate?: (screen: string) => void;
}

export default function TopBar({ title = "VitaSense AI", userName = "Samantha W." }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-outline-variant/20 bg-surface/82 px-4 shadow-sm shadow-black/[0.03] backdrop-blur-xl sm:px-6">
      <div className="flex items-center gap-4">
        <span className="text-lg font-black tracking-tight text-primary sm:text-xl">{title}</span>
        <span className="hidden items-center gap-1.5 rounded-full border border-primary/10 bg-primary/5 px-3 py-1 text-[10px] font-black uppercase tracking-wide text-primary lg:inline-flex">
          <ShieldCheck className="h-3.5 w-3.5" />
          Secure
        </span>
      </div>

      <div className="flex items-center gap-3 sm:gap-5">
        <label className="hidden h-10 w-72 items-center gap-2 rounded-full border border-outline-variant/20 bg-white/80 px-4 shadow-sm shadow-black/[0.03] transition-all duration-200 focus-within:border-primary/35 focus-within:ring-4 focus-within:ring-primary/10 md:flex">
          <Search className="w-4 h-4 text-on-surface-variant" />
          <input 
            className="bg-transparent border-none focus:outline-none text-xs w-full placeholder:text-on-surface-variant/50" 
            placeholder="Search data..." 
            type="text"
          />
        </label>

        <div className="flex items-center gap-4">
          <button
            type="button"
            aria-label="Notifications"
            className="relative rounded-full border border-outline-variant/20 bg-white/80 p-2.5 shadow-sm shadow-black/[0.03] transition-all duration-200 hover:border-primary/30 hover:bg-primary/5 active:scale-95"
          >
            <Bell className="w-5 h-5 text-on-surface-variant" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border border-surface"></span>
          </button>
          
          <div className="h-8 w-px bg-outline-variant/30 hidden sm:block"></div>

          <div className="flex items-center gap-3">
            <img 
              alt={userName} 
              className="h-9 w-9 rounded-full border-2 border-primary-fixed object-cover shadow-sm" 
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
