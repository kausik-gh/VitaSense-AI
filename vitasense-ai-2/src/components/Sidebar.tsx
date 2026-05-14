import {
  LayoutDashboard, 
  CalendarCheck, 
  MessageSquare, 
  Map,
  UserCircle, 
  HelpCircle, 
  LogOut, 
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  activeScreen: string;
  onNavigate: (screen: string) => void;
}

export default function Sidebar({ activeScreen, onNavigate }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'routine', label: 'Daily Routine', icon: CalendarCheck },
    { id: 'chatbot', label: 'Chatbot', icon: MessageSquare },
    { id: 'calendar', label: 'Area Map', icon: Map },
    { id: 'profile', label: 'Profile', icon: UserCircle },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-white/10 bg-[#0f1714] py-8 shadow-2xl shadow-black/25 md:flex">
      <div className="mb-12 px-6">
        <h1 className="text-xl font-black tracking-tight text-[#aff0d6]">VitaSense AI</h1>
        <p className="mt-1 text-[10px] font-black uppercase tracking-widest text-white/30">Predictive health OS</p>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            aria-pressed={activeScreen === item.id}
            className={`group relative mx-auto flex w-[88%] items-center rounded-2xl px-4 py-3 transition-all duration-200 active:scale-[0.98] ${
              activeScreen === item.id 
                ? 'bg-[#aff0d6] text-[#002117] shadow-xl shadow-[#aff0d6]/10' 
                : 'text-zinc-400 hover:bg-white/7 hover:text-white'
            }`}
          >
            {activeScreen === item.id && <span className="absolute -left-3 h-6 w-1 rounded-full bg-[#aff0d6]" />}
            <item.icon className="mr-3 w-5 h-5" />
            <span className="text-sm font-bold">{item.label}</span>
            <ChevronRight className={`ml-auto h-4 w-4 transition-all duration-200 ${activeScreen === item.id ? 'opacity-70' : 'opacity-0 group-hover:translate-x-0.5 group-hover:opacity-60'}`} />
          </button>
        ))}
      </nav>

      <div className="px-6 mt-auto space-y-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4 shadow-xl shadow-black/10">
          <div className="flex items-center gap-3 mb-3">
            <img 
              alt="Samantha W." 
              className="w-10 h-10 rounded-full bg-[#aff0d6] object-cover" 
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop"
            />
            <div>
              <p className="text-white text-xs font-bold leading-tight">Samantha W.</p>
              <p className="text-zinc-500 text-[10px]">Health Score: 80%</p>
            </div>
          </div>
          <button 
            onClick={() => onNavigate('onboarding')}
            className="w-full rounded-xl bg-[#2a6955] px-4 py-2.5 text-[10px] font-black uppercase tracking-wide text-white transition-all duration-200 hover:bg-[#347c65] active:scale-[0.98]"
          >
            Check your condition
          </button>
        </div>

        <div className="space-y-1">
          <button className="flex w-full items-center rounded-xl px-4 py-2 text-zinc-400 transition-all duration-200 hover:bg-white/7 hover:text-white">
            <HelpCircle className="mr-3 w-4 h-4" />
            <span className="text-xs font-medium">Help</span>
          </button>
          <button 
            onClick={() => onNavigate('welcome')}
            className="flex w-full items-center rounded-xl px-4 py-2 text-zinc-400 transition-all duration-200 hover:bg-white/7 hover:text-white"
          >
            <LogOut className="mr-3 w-4 h-4" />
            <span className="text-xs font-medium">Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
