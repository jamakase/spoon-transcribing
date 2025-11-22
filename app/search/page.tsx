'use client';

import Link from 'next/link';
import { Search, Filter, ChevronDown, Lock } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useNeoWallet } from '../context/NeoWalletContext';
import { api, Meeting } from '../services/api';

interface UIMeeting {
  id: string;
  title: string;
  date: string;
  status: string;
  tags: string[];
}

export default function SearchPage() {
  const { isConnected, address } = useNeoWallet();
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);
  
  const [meetings, setMeetings] = useState<UIMeeting[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function fetchMeetings() {
      if (!isConnected || !address) return;
      
      setIsLoading(true);
      try {
        const data = await api.getMeetings(address);
        const formattedMeetings: UIMeeting[] = data.map((m: Meeting) => ({
          id: String(m.id),
          title: m.title || 'Untitled Meeting',
          date: new Date(m.date || m.created_at).toLocaleDateString(),
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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setIsFilterOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredMeetings = meetings.filter(m => {
    const matchesQuery = m.title.toLowerCase().includes(query.toLowerCase()) || m.id.toLowerCase().includes(query.toLowerCase());
    const matchesFilter = filter === 'All' || m.status === filter;
    return matchesQuery && matchesFilter;
  });

  const FILTER_OPTIONS = ['All', 'ANALYZED', 'PROCESSING'];

  if (!isConnected) {
    return (
      <div className="p-8 text-slate-200 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800 animate-pulse mx-auto">
            <Lock className="w-10 h-10 text-neon-yellow" />
          </div>
          <h1 className="text-3xl font-display font-bold uppercase mb-3">Access Restricted</h1>
          <p className="text-slate-400 max-w-md">
             Please connect your Neo wallet to search through your encrypted meeting logs.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 text-slate-200 h-full flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold uppercase mb-6">Search Logs</h1>
        
        {/* Search Bar */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search by title, ID, or tag..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 pl-12 pr-4 py-4 text-white placeholder-slate-600 focus:border-neon-yellow outline-none"
            />
          </div>
          <div className="relative" ref={filterRef}>
            <button 
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={`px-6 py-4 bg-slate-900 border text-slate-400 hover:text-white flex items-center gap-2 transition-colors ${isFilterOpen ? 'border-neon-yellow text-white' : 'border-slate-800'}`}
            >
              <Filter className="w-4 h-4" />
              <span>{filter === 'All' ? 'Filter' : filter}</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${isFilterOpen ? 'rotate-180' : ''}`} />
            </button>
            
            {isFilterOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-slate-950 border border-slate-800 shadow-xl z-20 animate-fade-in-up">
                <div className="py-1">
                  {FILTER_OPTIONS.map((option) => (
                    <button
                      key={option}
                      onClick={() => {
                        setFilter(option);
                        setIsFilterOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 text-xs uppercase tracking-wider flex items-center justify-between hover:bg-slate-900 ${
                        filter === option ? 'text-neon-yellow' : 'text-slate-400'
                      }`}
                    >
                      {option}
                      {filter === option && <div className="w-1.5 h-1.5 bg-neon-yellow rounded-full" />}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-slate-900/50 border border-slate-800 flex-1 overflow-hidden flex flex-col">
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-slate-800 text-xs font-mono text-slate-500 uppercase tracking-widest bg-slate-950/50 shrink-0">
          <div className="col-span-2">ID</div>
          <div className="col-span-6">Subject</div>
          <div className="col-span-2">Date</div>
          <div className="col-span-2">Status</div>
        </div>

        <div className="overflow-y-auto divide-y divide-slate-800">
          {isLoading ? (
             <div className="p-12 text-center text-slate-500 font-mono uppercase">Loading...</div>
          ) : (
            <>
              {filteredMeetings.map((meeting) => (
                <div 
                  key={meeting.id} 
                  className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-slate-900 transition-colors group"
                >
                  <div className="col-span-2 font-mono text-sm text-slate-400 group-hover:text-neon-yellow transition-colors">
                    {meeting.id}
                  </div>
                  <div className="col-span-6">
                    <Link href={`/meetings/${meeting.id}`} className="block">
                      <div className="font-bold text-slate-200 group-hover:text-white transition-colors text-lg">
                        {meeting.title}
                      </div>
                      <div className="flex gap-2 mt-1">
                        {meeting.tags.map((tag) => (
                          <span key={tag} className="text-[10px] uppercase px-1.5 py-0.5 border border-slate-700 text-slate-500 rounded-sm">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </Link>
                  </div>
                  <div className="col-span-2 text-sm text-slate-400 font-mono">
                    {meeting.date}
                  </div>
                  <div className="col-span-2">
                    <span className={`inline-flex items-center gap-2 px-2 py-1 text-[10px] font-mono border uppercase ${
                      meeting.status === 'PROCESSING' 
                        ? 'border-yellow-500/30 text-yellow-500 bg-yellow-500/5 animate-pulse' 
                        : 'border-emerald-500/30 text-emerald-500 bg-emerald-500/5'
                    }`}>
                      {meeting.status}
                    </span>
                  </div>
                </div>
              ))}
              {filteredMeetings.length === 0 && (
                <div className="p-12 text-center text-slate-500 italic">
                  No logs found matching your query.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
