'use client';

import { useState } from 'react';
import { Link as LinkIcon, Mic, Video, Lock } from 'lucide-react';
import { api } from '../services/api';
import { useNeoWallet } from '../context/NeoWalletContext';

export default function RecordPage() {
  const { isConnected, address } = useNeoWallet();
  const [url, setUrl] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    if (!isConnected || !address) {
      alert('Please connect your wallet first.');
      return;
    }
    
    setIsRecording(true);
    try {
      await api.startRecallBot(url, 'Meeting Recording', address);
      alert(`Bot dispatched to: ${url}`);
      setUrl('');
    } catch (error: any) {
      console.error(error);
      alert(`Failed to dispatch bot: ${error.message || 'Unknown error'}`);
    } finally {
      setIsRecording(false);
    }
  };

  if (!isConnected) {
    return (
      <div className="p-8 text-slate-200 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800 animate-pulse mx-auto">
            <Lock className="w-10 h-10 text-neon-yellow" />
          </div>
          <h1 className="text-3xl font-display font-bold uppercase mb-3">Authentication Required</h1>
          <p className="text-slate-400 max-w-md">
            Connect your wallet to dispatch recording bots. This ensures all recordings are encrypted to your identity.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 text-slate-200 h-full flex items-center justify-center">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold uppercase mb-2">Record your meetings</h1>
          <p className="text-slate-400">Paste a meeting link to dispatch an AI notetaker instantly.</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-8 shadow-2xl relative overflow-hidden group">
          {/* Background Effect */}
          <div className="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none" />
          
          <h2 className="text-sm font-bold uppercase mb-4 flex items-center gap-2">
            <LinkIcon className="w-4 h-4 text-neon-yellow" />
            Record using meeting link
          </h2>

          <form onSubmit={handleStart} className="flex gap-0 relative z-10">
            <div className="flex-1 relative">
              <input 
                type="text" 
                placeholder="Paste meeting URL (Zoom, Google Meet, or Microsoft Teams)" 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full h-14 bg-slate-950 border border-slate-700 pl-4 pr-4 text-white placeholder-slate-600 focus:border-neon-yellow focus:ring-1 focus:ring-neon-yellow outline-none transition-all rounded-l-sm"
              />
            </div>
            <button 
              type="submit"
              disabled={!url || isRecording}
              className={`h-14 px-8 font-bold uppercase tracking-wider flex items-center gap-2 transition-all rounded-r-sm ${
                isRecording 
                  ? 'bg-slate-800 text-slate-500 cursor-wait' 
                  : 'bg-neon-yellow text-black hover:bg-[#b3e600]'
              }`}
            >
              {isRecording ? (
                'Dispatching...'
              ) : (
                <>
                  <div className="w-3 h-3 border-2 border-current rounded-full" />
                  Start Recording
                </>
              )}
            </button>
          </form>

          <div className="mt-6 flex gap-4 text-xs text-slate-500 font-mono uppercase">
            <span className="flex items-center gap-1"><Video className="w-3 h-3" /> Zoom</span>
            <span className="flex items-center gap-1"><Video className="w-3 h-3" /> Google Meet</span>
            <span className="flex items-center gap-1"><Video className="w-3 h-3" /> Teams</span>
          </div>
        </div>
      </div>
    </div>
  );
}
