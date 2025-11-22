'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Play, MoreHorizontal, Calendar, Clock, Activity, HardDrive, Cpu, Trash2, Edit, Share2, Sparkles, Bookmark, History, Lock, Send, X, Loader2 } from 'lucide-react';
import { api, Meeting } from './services/api';
import { useNeoWallet } from './context/NeoWalletContext';
import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';

const API_BASE_URL = '/api/proxy';

const STATS = [
  { label: 'Total Recordings', value: '124', sub: 'ARCHIVED', icon: HardDrive },
  { label: 'Action Items', value: '42', sub: 'PENDING', icon: Activity },
  { label: 'System Load', value: '12%', sub: 'OPTIMAL', icon: Cpu },
];

interface UIMeeting {
  id: string | number;
  title: string;
  date: string;
  duration: string;
  status: string;
  tags: string[];
}

function SystemClock() {
  const [time, setTime] = useState<Date | null>(null);

  useEffect(() => {
    setTime(new Date());
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  if (!time) {
    return <div className="text-4xl font-mono font-bold text-slate-800">--:--<span className="text-neon-yellow">.</span>--</div>;
  }

  const hours = time.getHours().toString().padStart(2, '0');
  const minutes = time.getMinutes().toString().padStart(2, '0');
  const seconds = time.getSeconds().toString().padStart(2, '0');

  return (
    <div className="text-4xl font-mono font-bold text-slate-700">
      {hours}:{minutes}<span className="text-neon-yellow animate-pulse">.</span>{seconds}
    </div>
  );
}

export default function Home() {
  const { isConnected, address } = useNeoWallet();
  const [activeMenu, setActiveMenu] = useState<string | number | null>(null);
  const [meetings, setMeetings] = useState<UIMeeting[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const [chatInput, setChatInput] = useState('');
  const { messages, sendMessage, status } = useChat({
    // transport: new TextStreamChatTransport({ api: `http://localhost:8001/api/chat` }),
    transport: new TextStreamChatTransport({ api: `https://api.transcribe.aprivai.com/api/chat` }),

  });
  const isChatLoading = status === 'streaming' || status === 'submitted';

  const onChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim()) {
      sendMessage({ text: chatInput });
      setChatInput('');
    }
  };

  useEffect(() => {
    async function fetchMeetings() {
      if (!isConnected || !address) return;
      
      setIsLoading(true);
      try {
        const data = await api.getMeetings(address);
        const formattedMeetings: UIMeeting[] = data.map((m: Meeting) => ({
          id: m.id,
          title: m.title || 'Untitled Meeting',
          date: new Date(m.date || m.created_at).toLocaleDateString(),
          duration: 'Unknown', 
          status: m.status || 'PROCESSING',
          tags: ['Meeting'] 
        }));
        setMeetings(formattedMeetings);
      } catch (error) {
        console.error('Failed to fetch meetings:', error);
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchMeetings();
  }, [isConnected, address]);

  // Click outside to close menu
  useEffect(() => {
    const handleClickOutside = () => setActiveMenu(null);
    window.addEventListener('click', handleClickOutside);
    return () => window.removeEventListener('click', handleClickOutside);
  }, []);

  // Scroll chat to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Open chat panel when there are messages
  useEffect(() => {
    if (messages.length > 0) {
      setIsChatOpen(true);
    }
  }, [messages.length]);

  if (!isConnected) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800 animate-pulse">
          <Lock className="w-10 h-10 text-neon-yellow" />
        </div>
        <h1 className="text-3xl font-display font-bold uppercase mb-3 text-white">Authentication Required</h1>
        <p className="text-slate-400 max-w-md mb-8">
          Access to Mission Control requires a secure connection. Please connect your Neo wallet to verify your identity and decrypt your transmissions.
        </p>
        <div className="text-xs font-mono text-slate-600 uppercase tracking-widest">
          Waiting for connection signal...
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 min-h-full text-slate-200 pb-32">
      {/* Header */}
      <header className="flex items-end justify-between mb-12 animate-fade-in-up">
        <div>
          <div className="text-xs font-mono text-neon-yellow mb-2 tracking-widest uppercase">:: System Status: Online</div>
          <h1 className="text-4xl md:text-5xl font-display font-bold uppercase tracking-tight text-white">
            Mission Control
          </h1>
        </div>
        <div className="hidden md:block text-right">
          <SystemClock />
          <div className="text-xs text-slate-500 uppercase tracking-widest">Local System Time</div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {STATS.map((stat, i) => (
          <div 
            key={stat.label} 
            className={`bg-slate-900 border border-slate-800 p-6 relative overflow-hidden group hover:border-neon-yellow transition-colors duration-300 animate-fade-in-up`}
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <stat.icon className="w-16 h-16 text-neon-yellow" />
            </div>
            <div className="relative z-10">
              <div className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">{stat.label}</div>
              <div className="text-4xl font-display font-bold text-white mb-2">{stat.value}</div>
              <div className="inline-flex items-center px-2 py-1 bg-slate-950 border border-slate-800 text-[10px] font-mono text-neon-yellow uppercase">
                {stat.sub}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent List */}
      <div className="animate-fade-in-up delay-300">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-display font-bold uppercase flex items-center gap-3">
            <span className="w-2 h-8 bg-neon-yellow block"></span>
            Recent Transmissions
          </h2>
          <Link href="/search" className="text-xs font-mono text-neon-yellow hover:underline uppercase tracking-widest">
            View All Logs
          </Link>
        </div>

        <div className="bg-slate-900/50 border border-slate-800">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 p-4 border-b border-slate-800 text-xs font-mono text-slate-500 uppercase tracking-widest bg-slate-950/50">
            <div className="col-span-2">ID</div>
            <div className="col-span-5">Subject</div>
            <div className="col-span-2">Date</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-1 text-right">Action</div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-slate-800">
            {isLoading ? (
              <div className="p-8 text-center text-slate-500 font-mono text-sm uppercase">
                Loading Transmissions...
              </div>
            ) : meetings.length === 0 ? (
              <div className="p-8 text-center text-slate-500 font-mono text-sm uppercase">
                No Transmissions Found
              </div>
            ) : (
              meetings.map((meeting) => (
                <div 
                  key={meeting.id} 
                  className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-slate-900 transition-colors group relative"
                >
                  <div className="col-span-2 font-mono text-sm text-slate-400 group-hover:text-neon-yellow transition-colors">
                    {meeting.id}
                  </div>
                  <div className="col-span-5">
                    <Link href={`/meetings/${meeting.id}`} className="block">
                      <div className="font-bold text-slate-200 group-hover:text-white transition-colors text-lg">
                        {meeting.title}
                      </div>
                      <div className="flex gap-2 mt-1">
                        {meeting.tags.map(tag => (
                          <span key={tag} className="text-[10px] uppercase px-1.5 py-0.5 border border-slate-700 text-slate-500 rounded-sm">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </Link>
                  </div>
                  <div className="col-span-2 text-sm text-slate-400 font-mono flex items-center gap-2">
                    <Calendar className="w-3 h-3" />
                    {meeting.date}
                  </div>
                  <div className="col-span-2">
                    <span className={`inline-flex items-center gap-2 px-2 py-1 text-[10px] font-mono border uppercase ${
                      meeting.status === 'PROCESSING' 
                        ? 'border-yellow-500/30 text-yellow-500 bg-yellow-500/5 animate-pulse' 
                        : 'border-emerald-500/30 text-emerald-500 bg-emerald-500/5'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        meeting.status === 'PROCESSING' ? 'bg-yellow-500' : 'bg-emerald-500'
                      }`}></span>
                      {meeting.status}
                    </span>
                  </div>
                  <div className="col-span-1 text-right flex justify-end relative">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenu(activeMenu === meeting.id ? null : meeting.id);
                      }}
                      className="p-2 hover:bg-slate-800 rounded-sm text-slate-500 hover:text-neon-yellow transition-colors"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {activeMenu === meeting.id && (
                      <div className="absolute right-0 top-full mt-1 w-32 bg-slate-950 border border-slate-800 shadow-xl z-20 animate-fade-in-up">
                        <div className="py-1">
                          <button className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-neon-yellow flex items-center gap-2">
                            <Share2 className="w-3 h-3" /> Share
                          </button>
                          <button className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-neon-yellow flex items-center gap-2">
                            <Edit className="w-3 h-3" /> Edit
                          </button>
                          <button className="w-full text-left px-3 py-2 text-xs text-red-400 hover:bg-slate-800 hover:text-red-300 flex items-center gap-2 border-t border-slate-800">
                            <Trash2 className="w-3 h-3" /> Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* AI Chat Interface */}
      <div className="fixed bottom-0 left-0 w-full pl-72 z-20 pointer-events-none">
        <div className="max-w-4xl mx-auto px-8 pb-8 pointer-events-auto">
          {/* Chat Messages Panel */}
          {isChatOpen && messages.length > 0 && (
            <div className="bg-slate-950 border border-slate-800 rounded-lg mb-3 shadow-2xl animate-fade-in-up">
              <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
                <span className="text-xs font-mono text-neon-yellow uppercase tracking-wider">AI Assistant</span>
                <button
                  onClick={() => setIsChatOpen(false)}
                  className="p-1 text-slate-500 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div
                ref={chatContainerRef}
                className="max-h-64 overflow-y-auto p-4 space-y-4"
              >
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-2 rounded-lg text-sm ${
                        message.role === 'user'
                          ? 'bg-neon-yellow text-black'
                          : 'bg-slate-800 text-slate-200'
                      }`}
                    >
                      {message.parts?.map((part, i) =>
                        part.type === 'text' ? <span key={i}>{part.text}</span> : null
                      ) || (message as any).content}
                    </div>
                  </div>
                ))}
                {isChatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-800 text-slate-200 px-4 py-2 rounded-lg text-sm flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Thinking...
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 mb-3 animate-fade-in-up delay-100">
            <span className="text-xs font-bold text-neon-yellow uppercase tracking-wider">Recommended:</span>
            <button
              onClick={() => sendMessage({ text: 'Catch me up on my recent meetings' })}
              className="flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-300 hover:border-neon-yellow hover:text-neon-yellow transition-colors"
            >
              <Clock className="w-3 h-3" /> Catch Me Up
            </button>
            <button
              onClick={() => sendMessage({ text: 'What are the key product insights from my meetings?' })}
              className="flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-300 hover:border-neon-yellow hover:text-neon-yellow transition-colors"
            >
              <Sparkles className="w-3 h-3" /> Product Insights
            </button>
          </div>

          <form id="chat-form" onSubmit={onChatSubmit} className="bg-slate-950 border border-slate-800 rounded-lg p-2 flex items-center gap-2 shadow-2xl animate-fade-in-up delay-200">
            <div className="pl-3">
              <Sparkles className="w-5 h-5 text-neon-yellow" />
            </div>
            <input
              id="chat-input"
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask anything about your meetings..."
              className="flex-1 bg-transparent border-none text-white placeholder-slate-500 focus:ring-0 focus:outline-none py-3"
            />
            <button
              type="submit"
              disabled={isChatLoading || !chatInput?.trim()}
              className="bg-neon-yellow hover:bg-[#b3e600] text-black font-bold px-6 py-2 rounded transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isChatLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Ask AI
            </button>
            <div className="h-8 w-px bg-slate-800 mx-1" />
            <button type="button" className="p-2 text-slate-500 hover:text-white transition-colors">
              <Bookmark className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => setIsChatOpen(!isChatOpen)}
              className={`p-2 transition-colors ${isChatOpen ? 'text-neon-yellow' : 'text-slate-500 hover:text-white'}`}
            >
              <History className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
