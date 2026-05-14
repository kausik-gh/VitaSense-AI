import { Search, Bell, LogOut } from 'lucide-react';

interface TopBarProps {
  title?: string;
  userName?: string;
  onNavigate?: (screen: string) => void;
}

export default function TopBar({ title = "VitaSense AI", userName = "Samantha W." }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 bg-surface/80 backdrop-blur-md shadow-sm h-16 w-full flex justify-between items-center px-6">
      <div className="flex items-center gap-4">
        <span className="text-xl font-bold text-primary">{title}</span>
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden md:flex bg-surface-container rounded-full px-4 py-2 items-center gap-2 w-64 ring-1 ring-black/5">
          <Search className="w-4 h-4 text-on-surface-variant" />
          <input 
            className="bg-transparent border-none focus:outline-none text-xs w-full placeholder:text-on-surface-variant/50" 
            placeholder="Search data..." 
            type="text"
          />
        </div>

        <div className="flex items-center gap-4">
          <button className="relative hover:bg-surface-container-high transition-colors p-2 rounded-full ring-1 ring-black/5">
            <Bell className="w-5 h-5 text-on-surface-variant" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border border-surface"></span>
          </button>
          
          <div className="h-8 w-px bg-outline-variant/30 hidden sm:block"></div>

          <div className="flex items-center gap-3">
            <img 
              alt={userName} 
              className="w-8 h-8 rounded-full border-2 border-primary-fixed object-cover" 
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
