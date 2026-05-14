import { ReactNode } from 'react';
import { CalendarCheck, LayoutDashboard, Map, MessageSquare, UserCircle } from 'lucide-react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

interface LayoutProps {
  children: ReactNode;
  activeScreen: string;
  onNavigate: (screen: string) => void;
  title?: string;
}

export default function Layout({ children, activeScreen, onNavigate, title }: LayoutProps) {
  const mobileItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'routine', label: 'Routine', icon: CalendarCheck },
    { id: 'calendar', label: 'Map', icon: Map },
    { id: 'chatbot', label: 'Chat', icon: MessageSquare },
    { id: 'profile', label: 'Profile', icon: UserCircle },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Sidebar activeScreen={activeScreen} onNavigate={onNavigate} />
      <main className="md:ml-64 min-h-screen flex flex-col pb-20 md:pb-0">
        <TopBar title={title} onNavigate={onNavigate} />
        <div className="flex-1 p-6 max-w-[1200px] mx-auto w-full">
          {children}
        </div>
      </main>
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-outline-variant/30 bg-white/92 px-3 py-2 shadow-2xl shadow-black/10 backdrop-blur-xl md:hidden">
        <div className="grid grid-cols-5 gap-1">
          {mobileItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 text-[10px] font-black uppercase tracking-wide transition-all ${
                activeScreen === item.id
                  ? 'bg-primary text-white shadow-lg shadow-primary/20'
                  : 'text-on-surface-variant hover:bg-surface-container'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}
