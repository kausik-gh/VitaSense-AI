const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export interface ChatStreamRequest {
  userId: number;
  sessionId: string;
  message: string;
  signal?: AbortSignal;
  onToken: (token: string) => void;
}

export async function streamChatMessage({
  userId,
  sessionId,
  message,
  signal,
  onToken,
}: ChatStreamRequest): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      session_id: sessionId,
      message,
    }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() ?? '';

    for (const event of events) {
      const payload = parseSseEvent(event);
      if (payload === null) continue;
      if (payload === '[DONE]') return;
      onToken(payload);
    }
  }

  if (buffer) {
    const payload = parseSseEvent(buffer);
    if (payload && payload !== '[DONE]') {
      onToken(payload);
    }
  }
}

function parseSseEvent(event: string): string | null {
  const dataLines = event
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.replace(/^data:\s?/, ''));

  if (dataLines.length === 0) {
    return null;
  }

  return dataLines.join('\n');
}
