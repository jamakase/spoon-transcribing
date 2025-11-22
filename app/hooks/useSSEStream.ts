import { useState, useEffect, useRef } from 'react';

export interface SSEMessage {
  type: string;
  data: any;
}

export function useSSEStream(url: string) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [status, setStatus] = useState<'idle' | 'connecting' | 'connected' | 'error' | 'closed'>('idle');
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = () => {
    if (eventSourceRef.current) return;

    setStatus('connecting');
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        // Assume the backend sends JSON strings in the 'data' field
        // Format: data: {"foo": "bar"}
        const parsedData = JSON.parse(event.data);
        setMessages(prev => [...prev, { type: 'message', data: parsedData }]);
      } catch (e) {
        // Handle plain text or non-JSON data
        setMessages(prev => [...prev, { type: 'message', data: event.data }]);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      setStatus('error');
      eventSource.close();
      eventSourceRef.current = null;
    };

    // If your backend sends custom named events (e.g. event: update)
    // you can listen to them like this:
    // eventSource.addEventListener('update', (e) => ...);
  };

  const close = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setStatus('closed');
    }
  };

  useEffect(() => {
    return () => {
      close();
    };
  }, []);

  return { messages, status, connect, close };
}

