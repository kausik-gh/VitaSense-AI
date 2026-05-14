import { useState } from 'react';
import { WelcomeScreen } from './screens/Welcome';
import { DashboardScreen } from './screens/Dashboard';
import { OnboardingScreen } from './screens/Onboarding';
import { DailyRoutineScreen } from './screens/DailyRoutine';
import { ProfileScreen } from './screens/Profile';
import { ChatbotScreen } from './screens/Chatbot';
import Layout from './components/Layout';
import { AnimatePresence } from 'motion/react';

type Screen = 'welcome' | 'dashboard' | 'onboarding' | 'routine' | 'profile' | 'chatbot' | 'calendar';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('welcome');

  const handleNavigate = (screen: string) => {
    setCurrentScreen(screen as Screen);
  };

  if (currentScreen === 'welcome') {
    return <WelcomeScreen onStart={() => setCurrentScreen('dashboard')} />;
  }

  if (currentScreen === 'onboarding') {
    return <OnboardingScreen onComplete={() => setCurrentScreen('dashboard')} onCancel={() => setCurrentScreen('dashboard')} />;
  }

  return (
    <Layout activeScreen={currentScreen} onNavigate={handleNavigate} title={
      currentScreen === 'routine' ? 'Daily Routine' : 
      currentScreen === 'chatbot' ? 'Chatbot' :
      currentScreen === 'profile' ? 'Profile' : 
      'VitaSense AI'
    }>
      <AnimatePresence mode="wait">
        {currentScreen === 'dashboard' && <DashboardScreen onAction={handleNavigate} />}
        {currentScreen === 'routine' && <DailyRoutineScreen />}
        {currentScreen === 'profile' && <ProfileScreen />}
        {currentScreen === 'chatbot' && <ChatbotScreen />}
        {currentScreen === 'calendar' && (
          <div className="flex items-center justify-center h-full">
            <p className="text-on-surface-variant font-bold opacity-30">Calendar View - Coming Soon</p>
          </div>
        )}
      </AnimatePresence>
    </Layout>
  );
}
