import { 
  LayoutDashboard, 
  CalendarCheck, 
  MessageSquare, 
  Map,
  UserCircle, 
  HelpCircle, 
  LogOut, 
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import { motion } from 'motion/react';

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
    <aside className="hidden md:flex flex-col h-screen fixed left-0 top-0 py-10 z-40 bg-zinc-900 w-64 rounded-r-3xl">
      <div className="px-6 mb-16">
        <h1 className="text-xl font-black text-[#aff0d6]">VitaSense AI</h1>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-[95%] mx-auto flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
              activeScreen === item.id 
                ? 'bg-[#7ab9a1] text-[#004a38] font-bold' 
                : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
            }`}
          >
            <item.icon className="mr-3 w-5 h-5" />
            <span className="text-sm font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="px-6 mt-auto space-y-4">
        <div className="p-4 bg-zinc-800/50 rounded-2xl border border-zinc-700/50">
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
            className="w-full py-2 px-4 bg-[#2a6955] text-white rounded-lg text-[10px] font-bold hover:opacity-90 transition-all"
          >
            Check your condition
          </button>
        </div>

        <div className="space-y-1">
          <button className="w-full text-zinc-400 flex items-center px-4 py-2 hover:text-white transition-all">
            <HelpCircle className="mr-3 w-4 h-4" />
            <span className="text-xs font-medium">Help</span>
          </button>
          <button 
            onClick={() => onNavigate('welcome')}
            className="w-full text-zinc-400 flex items-center px-4 py-2 hover:text-white transition-all"
          >
            <LogOut className="mr-3 w-4 h-4" />
            <span className="text-xs font-medium">Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
