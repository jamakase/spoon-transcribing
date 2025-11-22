'use client';

import { useMeetingStream } from '../hooks/useMeetingStream';

export default function SSEPage() {
  // TODO: Replace '123' with a valid meeting ID from your backend
  const { messages, status, connect, close } = useMeetingStream('123');

  return (
    <div className="p-8 text-slate-800 font-sans max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Meeting Stream Debugger</h1>
        <div className="flex gap-2">
          <button 
            onClick={connect} 
            disabled={status === 'connected' || status === 'connecting'}
            className="px-4 py-2 bg-slate-900 text-white rounded hover:bg-slate-800 disabled:opacity-50 transition-colors text-sm font-medium"
          >
            Connect Stream
          </button>
          <button 
            onClick={close} 
            disabled={status === 'closed' || status === 'idle'}
            className="px-4 py-2 border border-slate-300 text-slate-700 rounded hover:bg-slate-50 disabled:opacity-50 transition-colors text-sm font-medium"
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className={`mb-6 p-3 rounded-md flex items-center gap-2 text-sm font-mono ${
        status === 'connected' ? 'bg-green-50 text-green-700 border border-green-200' :
        status === 'error' ? 'bg-red-50 text-red-700 border border-red-200' :
        'bg-slate-50 text-slate-600 border border-slate-200'
      }`}>
        <div className={`w-2 h-2 rounded-full ${
          status === 'connected' ? 'bg-green-500 animate-pulse' :
          status === 'error' ? 'bg-red-500' :
          'bg-slate-400'
        }`} />
        STATUS: {status.toUpperCase()}
      </div>

      {/* Stream Log */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 text-xs font-bold text-slate-500 uppercase tracking-wider">
          Live Events
        </div>
        <div className="h-[500px] overflow-y-auto p-4 space-y-3 bg-slate-50/50">
          {messages.length === 0 && (
            <div className="text-center text-slate-400 py-12 italic">
              No events received yet. Connect to start streaming.
            </div>
          )}
          
          {messages.map((msg, i) => (
            <div key={i} className="animate-fade-in-up">
              {msg.type === 'transcript' ? (
                <div className="flex gap-3 bg-white p-3 rounded border border-slate-100 shadow-sm">
                  <div className="w-16 shrink-0 text-xs font-bold text-slate-500 pt-1">
                    {msg.data.speaker || 'UNK'}
                  </div>
                  <div className="text-sm text-slate-800">
                    {msg.data.text}
                  </div>
                </div>
              ) : (
                <div className="flex gap-3 bg-slate-100 p-2 rounded border border-slate-200 text-xs font-mono text-slate-600">
                  <span className="uppercase font-bold text-slate-400">{msg.type}</span>
                  <span className="truncate">{JSON.stringify(msg.data)}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
