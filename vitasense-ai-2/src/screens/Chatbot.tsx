import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  AlertCircle,
  Bot,
  Brain,
  CheckCircle2,
  Loader2,
  MessageCircle,
  RefreshCw,
  Send as SendIcon,
  ShieldCheck,
  Sparkles,
  User,
} from 'lucide-react';
import { DEMO_USER_ID } from '../lib/demoData';
import { streamChatMessage } from '../lib/chat';

type ChatRole = 'assistant' | 'user';
type StreamState = 'idle' | 'streaming' | 'error';

interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  status?: 'streaming' | 'complete' | 'failed';
}

const SESSION_KEY = 'vitasense.chat.sessionId';
const MESSAGES_KEY = 'vitasense.chat.messages';

const initialAssistantMessage: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    "Good morning, Samantha. I can connect what you're feeling with your recent sleep, activity, hydration, and environmental context. Tell me what changed today.",
  createdAt: new Date().toISOString(),
  status: 'complete',
};

function createSessionId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getStoredSessionId() {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;
  const next = createSessionId();
  localStorage.setItem(SESSION_KEY, next);
  return next;
}

function getStoredMessages() {
  try {
    const raw = localStorage.getItem(MESSAGES_KEY);
    if (!raw) return [initialAssistantMessage];
    const parsed = JSON.parse(raw) as ChatMessage[];
    return parsed.length ? parsed : [initialAssistantMessage];
  } catch {
    return [initialAssistantMessage];
  }
}

function formatTime(iso: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso));
}

function MessageContent({ text }: { text: string }) {
  const lines = text.split('\n').filter((line) => line.trim().length > 0);

  return (
    <div className="space-y-3">
      {lines.map((line, index) => {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
          return (
            <div key={`${trimmed}-${index}`} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-current opacity-50" />
              <p className="text-sm font-medium leading-7">{trimmed.slice(2)}</p>
            </div>
          );
        }
        return (
          <p key={`${trimmed}-${index}`} className="text-sm font-medium leading-7">
            {trimmed}
          </p>
        );
      })}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map((dot) => (
        <span
          key={dot}
          className="h-2 w-2 rounded-full bg-primary/60"
          style={{ animation: `pulse 1.2s ease-in-out ${dot * 0.18}s infinite` }}
        />
      ))}
    </div>
  );
}

export function ChatbotScreen() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([initialAssistantMessage]);
  const [draft, setDraft] = useState('');
  const [streamState, setStreamState] = useState<StreamState>('idle');
  const [errorText, setErrorText] = useState('');
  const [lastUserMessage, setLastUserMessage] = useState('');
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    setSessionId(getStoredSessionId());
    setMessages(getStoredMessages());
  }, []);

  useEffect(() => {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages.slice(-30)));
  }, [messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, streamState]);

  const latestAssistantState = useMemo(() => {
    const latest = [...messages].reverse().find((message) => message.role === 'assistant');
    return latest?.status ?? 'complete';
  }, [messages]);

  const sendMessage = async (messageText: string) => {
    const cleanMessage = messageText.trim();
    if (!cleanMessage || streamState === 'streaming' || !sessionId) return;

    const userMessage: ChatMessage = {
      id: createSessionId(),
      role: 'user',
      content: cleanMessage,
      createdAt: new Date().toISOString(),
      status: 'complete',
    };
    const assistantId = createSessionId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      createdAt: new Date().toISOString(),
      status: 'streaming',
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setDraft('');
    setLastUserMessage(cleanMessage);
    setErrorText('');
    setStreamState('streaming');

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await streamChatMessage({
        userId: DEMO_USER_ID,
        sessionId,
        message: cleanMessage,
        signal: controller.signal,
        onToken: (token) => {
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantId
                ? { ...item, content: item.content + token, status: 'streaming' }
                : item,
            ),
          );
        },
      });

      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content:
                  item.content ||
                  "I couldn't generate a response. Please try again in a moment.",
                status: 'complete',
              }
            : item,
        ),
      );
      setStreamState('idle');
    } catch {
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content:
                  "I couldn't reach VitaSense intelligence right now. Your message stayed on this device; please retry once the backend is available.",
                status: 'failed',
              }
            : item,
        ),
      );
      setErrorText('Connection interrupted. Retry will resend your last message with the same session.');
      setStreamState('error');
    } finally {
      abortRef.current = null;
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void sendMessage(draft);
  };

  const handleRetry = () => {
    if (lastUserMessage) {
      void sendMessage(lastUserMessage);
    }
  };

  const resetSession = () => {
    abortRef.current?.abort();
    const nextSession = createSessionId();
    localStorage.setItem(SESSION_KEY, nextSession);
    localStorage.setItem(MESSAGES_KEY, JSON.stringify([initialAssistantMessage]));
    setSessionId(nextSession);
    setMessages([initialAssistantMessage]);
    setDraft('');
    setStreamState('idle');
    setErrorText('');
    setLastUserMessage('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex h-[calc(100vh-112px)] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-2xl shadow-black/5"
    >
      <header className="border-b border-surface-container bg-[#101715] px-5 py-5 text-white sm:px-7">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#aff0d6] text-[#002117] shadow-xl shadow-primary/20">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-black tracking-normal">VitaSense Companion</h1>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-[#aff0d6]">
                  <Sparkles className="h-3.5 w-3.5" />
                  Context aware
                </span>
              </div>
              <p className="mt-2 max-w-2xl text-sm font-medium leading-6 text-white/58">
                Ask about symptoms, energy, sleep, food, stress, or environmental patterns. Safety checks run before guidance reaches you.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-4 py-2 text-xs font-bold text-white/70">
              {streamState === 'streaming' ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4 text-[#94d4bb]" />}
              {streamState === 'streaming' ? 'Thinking' : 'Ready'}
            </div>
            <button
              type="button"
              onClick={resetSession}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-4 py-2 text-xs font-bold text-white/70 transition-colors hover:bg-white/12"
            >
              <RefreshCw className="h-4 w-4" />
              New session
            </button>
          </div>
        </div>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[1fr_280px]">
        <section className="flex min-h-0 flex-col bg-surface/40">
          <div className="custom-scrollbar min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-6 sm:px-7">
            <AnimatePresence initial={false}>
              {messages.map((message) => {
                const isUser = message.role === 'user';
                return (
                  <motion.article
                    key={message.id}
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
                  >
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl shadow-lg ${
                        isUser ? 'bg-primary text-white' : 'bg-[#aff0d6] text-[#002117]'
                      }`}
                    >
                      {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                    </div>

                    <div className={`max-w-[min(88%,720px)] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
                      <div
                        className={`rounded-2xl px-5 py-4 shadow-xl shadow-black/5 ${
                          isUser
                            ? 'rounded-tr-none bg-primary text-white'
                            : message.status === 'failed'
                            ? 'rounded-tl-none border border-error/20 bg-error-container/70 text-on-error-container'
                            : 'rounded-tl-none border border-white bg-white text-on-surface'
                        }`}
                      >
                        {message.status === 'streaming' && !message.content ? (
                          <TypingIndicator />
                        ) : (
                          <MessageContent text={message.content} />
                        )}
                      </div>
                      <span className={`mt-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant/35 ${isUser ? 'text-right' : ''}`}>
                        {formatTime(message.createdAt)}
                      </span>
                    </div>
                  </motion.article>
                );
              })}
            </AnimatePresence>
            <div ref={bottomRef} />
          </div>

          <AnimatePresence>
            {errorText && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
                className="mx-4 mb-4 flex flex-col gap-3 rounded-2xl border border-error/20 bg-error-container/70 p-4 text-on-error-container sm:mx-7 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
                  <p className="text-sm font-bold leading-6">{errorText}</p>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  disabled={streamState === 'streaming'}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-on-error-container px-4 py-2 text-xs font-black text-white transition-transform hover:scale-[1.02] disabled:opacity-50"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          <footer className="border-t border-surface-container bg-white p-4 sm:p-6">
            <form onSubmit={handleSubmit} className="flex items-end gap-3">
              <div className="min-w-0 flex-1 rounded-[1.5rem] bg-surface-container px-5 py-3 ring-1 ring-black/5 transition-all focus-within:ring-2 focus-within:ring-primary/30">
                <label htmlFor="chat-message" className="sr-only">
                  Message VitaSense Companion
                </label>
                <textarea
                  id="chat-message"
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault();
                      event.currentTarget.form?.requestSubmit();
                    }
                  }}
                  disabled={streamState === 'streaming'}
                  rows={1}
                  className="max-h-32 min-h-10 w-full resize-none bg-transparent text-sm font-semibold leading-6 text-on-surface placeholder:text-on-surface-variant/40 focus:outline-none disabled:opacity-60"
                  placeholder="Tell VitaSense what changed today..."
                />
              </div>
              <button
                type="submit"
                disabled={!draft.trim() || streamState === 'streaming'}
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary text-white shadow-xl shadow-primary/20 transition-transform hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-45"
                aria-label="Send message"
              >
                {streamState === 'streaming' ? <Loader2 className="h-5 w-5 animate-spin" /> : <SendIcon className="h-5 w-5" />}
              </button>
            </form>

            <div className="mt-4 flex flex-wrap gap-2">
              {['Why is my energy low?', 'Check sleep and hydration', 'Could today’s AQI affect me?'].map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => setDraft(prompt)}
                  disabled={streamState === 'streaming'}
                  className="rounded-full border border-outline-variant/30 bg-white px-4 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface transition-all hover:border-primary hover:bg-primary/5 disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </footer>
        </section>

        <aside className="hidden border-l border-surface-container bg-white p-6 lg:block">
          <div className="space-y-5">
            <div className="rounded-2xl bg-[#101715] p-5 text-white">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-2xl bg-[#aff0d6] text-[#002117]">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <p className="text-sm font-black">Medical safety layer</p>
              <p className="mt-2 text-xs font-semibold leading-5 text-white/55">
                Emergency detection, diagnosis blocking, and disclaimer enforcement run through the backend.
              </p>
            </div>

            <div className="rounded-2xl border border-outline-variant/20 bg-surface p-5">
              <div className="mb-3 flex items-center gap-2">
                <MessageCircle className="h-4 w-4 text-primary" />
                <p className="text-xs font-black uppercase tracking-widest text-on-surface-variant/55">Session</p>
              </div>
              <p className="break-all text-xs font-bold leading-5 text-on-surface-variant">
                {sessionId || 'Preparing session...'}
              </p>
            </div>

            <div className="rounded-2xl border border-outline-variant/20 bg-white p-5 shadow-xl shadow-black/5">
              <p className="text-xs font-black uppercase tracking-widest text-on-surface-variant/50">Companion memory</p>
              <p className="mt-3 text-sm font-semibold leading-6 text-on-surface-variant">
                Last {Math.max(messages.length - 1, 0)} messages are kept locally for continuity on this device.
              </p>
            </div>
          </div>
        </aside>
      </main>
    </motion.div>
  );
}
