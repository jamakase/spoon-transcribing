import { useState, useEffect, useRef } from 'react';

export interface TranscriptSegment {
  speaker: string;
  text: string;
  timestamp: string;
}

export interface SSEMessage {
  type: 'transcript' | 'status' | 'error' | 'summary' | 'action_item';
  data: any;
}

export function useMeetingStream(meetingId: string | null) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [status, setStatus] = useState<'idle' | 'connecting' | 'connected' | 'error' | 'closed'>('idle');
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = () => {
    if (!meetingId || eventSourceRef.current) return;

    // NOTE: The docs don't explicitly show the SSE endpoint URL structure.
    // Assuming a standard pattern like /streaming/meetings/{id}/events based on the other endpoints.
    // You MUST verify this exact URL path with your backend developer.
    const streamUrl = `YOUR_API_BASE_URL/streaming/meetings/${meetingId}/events`; 

    setStatus('connecting');
    const eventSource = new EventSource(streamUrl);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        // Expecting standard SSE format:
        // data: {"type": "transcript", "data": {...}}
        const parsed = JSON.parse(event.data);
        setMessages(prev => [...prev, parsed]);
      } catch (e) {
        console.warn('Failed to parse SSE message', event.data);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      setStatus('error');
      eventSource.close();
      eventSourceRef.current = null;
    };
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

