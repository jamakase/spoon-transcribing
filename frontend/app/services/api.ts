const API_BASE_URL = '/api/proxy';

export interface ActionItem {
  task: string;
  assignee: string;
  deadline: string;
}

export interface Summary {
  id: number;
  text: string;
  action_items: ActionItem[];
  decisions: string[];
  created_at: string;
}

export interface TranscriptSegment {
  [key: string]: any;
}

export interface Transcript {
  id: number;
  text: string;
  segments: Record<string, any>;
  created_at: string;
}

export interface Meeting {
  id: number;
  title: string;
  date: string;
  status: string;
  created_at: string;
}

export interface MeetingDetail extends Meeting {
  audio_url?: string;
  transcript?: Transcript;
  summary?: Summary;
  participants?: string[];
}

export const api = {
  async getMeetings(publicKey?: string): Promise<Meeting[]> {
    const headers: Record<string, string> = { 'Accept': 'application/json' };
    if (publicKey) {
      headers['x-user-pubkey'] = publicKey;
    }
    
    const res = await fetch(`${API_BASE_URL}/meetings`, {
      headers,
      cache: 'no-store',
    });
    if (!res.ok) throw new Error('Failed to fetch meetings');
    return res.json();
  },

  async getMeeting(id: number | string, publicKey?: string): Promise<MeetingDetail> {
    const headers: Record<string, string> = { 'Accept': 'application/json' };
    if (publicKey) {
      headers['x-user-pubkey'] = publicKey;
    }

    const res = await fetch(`${API_BASE_URL}/meetings/${id}`, {
      headers,
      cache: 'no-store',
    });
    if (!res.ok) throw new Error('Failed to fetch meeting details');
    return res.json();
  },

  async startRecallBot(url: string, title: string = 'Meeting Recording', publicKey?: string): Promise<any> {
    const headers: Record<string, string> = {
      'Accept': 'application/json',
    };
    if (publicKey) {
      headers['x-user-pubkey'] = publicKey;
    }

    const formData = new FormData();
    formData.append('meeting_url', url);
    formData.append('title', title);

    const res = await fetch(`${API_BASE_URL}/meetings`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail?.[0]?.msg || errorData.detail || 'Failed to start bot');
    }
    return res.json();
  }
};
