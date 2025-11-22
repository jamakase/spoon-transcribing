'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ChevronLeft, 
  Play, 
  Download, 
  Share2, 
  CheckSquare, 
  User, 
  Brain, 
  Search,
  Lock
} from 'lucide-react';
import { api, MeetingDetail as MeetingDetailType } from '../../services/api';
import { useNeoWallet } from '../../context/NeoWalletContext';

// Since we need client-side logic for wallet, we'll make the main component client-side
// fetching is moved to the client.

export default function MeetingDetail({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState<string>('');
  
  useEffect(() => {
    params.then(p => setId(p.id));
  }, [params]);

  if (!id) return null;

  return <MeetingDetailClient id={id} />;
}

function MeetingDetailClient({ id }: { id: string }) {
  const { isConnected, address } = useNeoWallet();
  const [meeting, setMeeting] = useState<MeetingDetailType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isConnected || !address) {
      setIsLoading(false);
      return;
    }

    async function fetchMeeting() {
      try {
        setIsLoading(true);
        const data = await api.getMeeting(id, address!);
        setMeeting(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load meeting details.');
      } finally {
        setIsLoading(false);
      }
    }

    fetchMeeting();
  }, [id, isConnected, address]);

  if (!isConnected) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800">
          <Lock className="w-8 h-8 text-slate-500" />
        </div>
        <h1 className="text-xl font-display font-bold uppercase mb-3 text-white">Access Restricted</h1>
        <p className="text-slate-400 max-w-md mb-8">
          Please connect your Neo wallet to view this meeting log.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400 font-mono uppercase">
        Loading Secure Log...
      </div>
    );
  }

  if (error || !meeting) {
     return (
       <div className="h-full flex items-center justify-center text-slate-400 font-mono uppercase">
         {error || 'Meeting not found'}
       </div>
     );
  }

  // Map Transcript
  let transcriptData: Array<{ speaker: string; time: string; text: string }> = [];
  
  if (meeting.transcript?.segments && Object.keys(meeting.transcript.segments).length > 0) {
    const segments = Object.values(meeting.transcript.segments);
    transcriptData = segments.map((s: any) => ({
      speaker: s.speaker || 'Unknown',
      time: s.start_time ? new Date(s.start_time * 1000).toISOString().substr(11, 8) : (s.time || '00:00:00'),
      text: s.text || ''
    }));
  } else if (meeting.transcript?.text) {
    transcriptData = [{
      speaker: 'System',
      time: '00:00:00',
      text: meeting.transcript.text
    }];
  }

  // Map Action Items
  const actionItems = meeting.summary?.action_items?.map((item, index) => ({
    id: index,
    text: item.task,
    owner: item.assignee || 'Unassigned',
    status: 'pending'
  })) || [];

  // Summary Text
  const summaryText = meeting.summary?.text || 'No summary available.';

  return (
    <div className="h-full flex flex-col overflow-hidden bg-slate-950 text-slate-200">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950 p-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 hover:bg-slate-900 rounded-sm text-slate-400 hover:text-neon-yellow transition-colors">
            <ChevronLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">
              <span>LOG: {id}</span>
              <span className={`w-1.5 h-1.5 rounded-full ${
                  meeting.status === 'PROCESSING' ? 'bg-yellow-500' : 'bg-emerald-500'
                }`} />
              <span>{meeting.status || 'UNKNOWN'}</span>
            </div>
            <h1 className="text-xl font-display font-bold text-white">{meeting.title || 'Untitled Meeting'}</h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-2 border border-slate-800 hover:border-neon-yellow hover:text-neon-yellow transition-colors text-xs font-mono uppercase tracking-wider">
            <Share2 className="w-3 h-3" />
            Share
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-neon-yellow text-black font-bold hover:bg-[#b3e600] transition-colors text-xs font-mono uppercase tracking-wider">
            <Download className="w-3 h-3" />
            Export
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left: Transcript */}
        <div className="flex-1 flex flex-col border-r border-slate-800 min-w-0">
          {/* Toolbar */}
          <div className="p-3 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button className="p-2 bg-neon-yellow text-black rounded-full hover:scale-105 transition-transform">
                <Play className="w-4 h-4 fill-current" />
              </button>
              <div className="h-8 w-64 bg-slate-800/50 relative overflow-hidden rounded-sm">
                {/* Fake waveform */}
                <div className="absolute inset-0 flex items-center justify-center gap-0.5 opacity-50">
                  {Array.from({ length: 40 }).map((_, i) => (
                    <div 
                      key={i} 
                      className="w-1 bg-neon-yellow" 
                      style={{ height: `${Math.random() * 100}%` }} 
                    />
                  ))}
                </div>
              </div>
              <span className="font-mono text-xs text-slate-400">00:00:00 / --:--:--</span>
            </div>
            <div className="flex items-center gap-2">
               <Search className="w-4 h-4 text-slate-500" />
               <input 
                 type="text" 
                 placeholder="SEARCH TRANSCRIPT..." 
                 className="bg-transparent border-none text-xs font-mono text-white placeholder-slate-600 focus:ring-0 w-48"
               />
            </div>
          </div>

          {/* Transcript Scroll */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {transcriptData.length > 0 ? (
              transcriptData.map((block, i) => (
                <div key={i} className="flex gap-6 group hover:bg-slate-900/50 -mx-6 px-6 py-4 transition-colors border-l-2 border-transparent hover:border-neon-yellow">
                  <div className="w-24 shrink-0 pt-1">
                    <div className="font-mono text-xs font-bold text-neon-yellow mb-1">{block.speaker}</div>
                    <div className="font-mono text-[10px] text-slate-600">{block.time}</div>
                  </div>
                  <div className="text-slate-300 leading-relaxed font-light text-lg">
                    {block.text}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-center py-10 font-mono uppercase">
                No transcript available yet.
              </div>
            )}
          </div>
        </div>

        {/* Right: Intelligence */}
        <div className="w-96 bg-slate-950 flex flex-col overflow-y-auto border-l border-slate-800">
          
          {/* Summary Module */}
          <div className="p-6 border-b border-slate-800">
            <div className="flex items-center gap-2 mb-4 text-neon-yellow">
              <Brain className="w-5 h-5" />
              <h2 className="font-display font-bold uppercase text-sm tracking-wider">AI Summary</h2>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed mb-4 whitespace-pre-wrap">
              {summaryText}
            </p>
            <div className="flex flex-wrap gap-2">
              {/* Mock tags for now */}
              <span className="text-[10px] font-mono uppercase px-2 py-1 border border-slate-800 text-slate-500">#Meeting</span>
            </div>
          </div>

          {/* Action Items Module */}
          <div className="p-6 border-b border-slate-800 flex-1">
            <div className="flex items-center gap-2 mb-4 text-neon-yellow">
              <CheckSquare className="w-5 h-5" />
              <h2 className="font-display font-bold uppercase text-sm tracking-wider">Action Items</h2>
            </div>
            <div className="space-y-3">
              {actionItems.length > 0 ? actionItems.map((item) => (
                <div key={item.id} className="p-3 border border-slate-800 bg-slate-900/30 hover:border-slate-600 transition-colors group">
                  <div className="flex items-start gap-3">
                    <div className={`w-4 h-4 mt-0.5 border flex items-center justify-center transition-colors ${
                      item.status === 'done' ? 'bg-neon-yellow border-neon-yellow' : 'border-slate-600'
                    }`}>
                      {item.status === 'done' && <div className="w-2 h-2 bg-black" />}
                    </div>
                    <div>
                      <p className={`text-sm mb-2 ${item.status === 'done' ? 'text-slate-500 line-through' : 'text-slate-200'}`}>
                        {item.text}
                      </p>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1 px-1.5 py-0.5 bg-slate-800 rounded-sm">
                          <User className="w-3 h-3 text-slate-400" />
                          <span className="text-[10px] font-mono text-slate-300 uppercase">{item.owner}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="text-xs text-slate-500 font-mono uppercase">No action items found.</div>
              )}
            </div>
          </div>

          {/* Participants Module */}
          <div className="p-6">
            <h2 className="font-mono text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Participants</h2>
            <div className="flex -space-x-2">
              {meeting.participants && meeting.participants.length > 0 ? (
                meeting.participants.map((p, i) => (
                  <div key={i} title={p} className="w-8 h-8 rounded-none bg-slate-800 border border-slate-950 flex items-center justify-center text-[10px] font-bold text-slate-400 hover:z-10 hover:scale-110 hover:bg-neon-yellow hover:text-black transition-all cursor-pointer">
                    {p[0].toUpperCase()}
                  </div>
                ))
              ) : (
                 <div className="text-xs text-slate-500">No participants info.</div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
