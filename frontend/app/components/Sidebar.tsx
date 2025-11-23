'use client';

import Link from 'next/link';
import { 
  Mic, 
  Search, 
  FileBarChart, 
  Zap, 
  Wallet,
  Settings,
  Bot
} from 'lucide-react';
import { useNeoWallet } from '../context/NeoWalletContext';

const NAV_ITEMS = [
  { label: 'Record Now', href: '/record', icon: Mic },
  { label: 'Search', href: '/search', icon: Search },
  { label: 'AI Reports', href: '/reports', icon: FileBarChart },
  { label: 'Digital Twins', href: '/digital-twins', icon: Bot },
  { label: 'Integrations', href: '/integrations', icon: Zap },
];

export function Sidebar() {
  const { address, isConnected, connect, disconnect } = useNeoWallet();

  const handleWalletClick = () => {
    if (isConnected) {
      if (window.confirm('Disconnect wallet?')) {
        disconnect();
      }
    } else {
      connect();
    }
  };

  return (
    <aside className="w-72 bg-slate-950 border-r border-slate-800 flex flex-col h-full flex-shrink-0 shadow-[4px_0_15px_rgba(0,0,0,0.5)] z-10">
      <Link href="/" className="p-6 border-b border-slate-800 flex items-center gap-3 hover:bg-slate-900 transition-colors">
        <div className="w-3 h-3 bg-neon-yellow rounded-none shadow-[0_0_8px_#ccff00]" />
        <h1 className="text-xl font-display font-bold tracking-wider uppercase text-slate-100">
          Wiped<span className="text-neon-yellow">.OS</span>
        </h1>
      </Link>

      <div className="px-4 py-4">
        <div className="text-xs font-mono text-slate-500 mb-2 uppercase tracking-widest pl-2">System Navigation</div>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="group flex items-center gap-3 px-3 py-3 text-sm font-medium transition-all hover:bg-slate-900 border-l-2 border-transparent hover:border-neon-yellow text-slate-400 hover:text-neon-yellow"
            >
              <item.icon className="w-4 h-4 transition-colors group-hover:text-neon-yellow" />
              <span className="tracking-wide">{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-4 border-t border-slate-800 bg-slate-900/30">
        {/* Wallet Connect Button / User Profile */}
        <div 
          onClick={handleWalletClick}
          className={`flex items-center justify-between px-3 py-2 border ${
            isConnected ? 'border-neon-yellow/50 bg-neon-yellow/10' : 'border-slate-800 bg-slate-950'
          } hover:border-neon-yellow transition-colors cursor-pointer group relative overflow-hidden`}
        >
          {isConnected && <div className="absolute top-0 right-0 w-2 h-2 bg-neon-yellow shadow-[0_0_5px_#ccff00]" />}
          
          <div className="flex items-center gap-3 overflow-hidden">
            <div className={`w-8 h-8 shrink-0 border flex items-center justify-center text-xs font-display font-bold ${
              isConnected ? 'bg-neon-yellow text-black border-neon-yellow' : 'bg-slate-800 border-slate-700 text-slate-500'
            }`}>
              {isConnected ? 'N3' : <Wallet className="w-4 h-4" />}
            </div>
            <div className="flex flex-col min-w-0">
              <span className={`text-sm font-medium truncate transition-colors ${
                isConnected ? 'text-neon-yellow' : 'text-slate-200 group-hover:text-neon-yellow'
              }`}>
                {isConnected ? `${address?.slice(0, 6)}...${address?.slice(-4)}` : 'Connect Wallet'}
              </span>
              <span className="text-[10px] text-slate-500 font-mono uppercase">
                {isConnected ? 'Neo N3 Network' : 'NeoLine Required'}
              </span>
            </div>
          </div>
          
          {!isConnected && <Settings className="w-4 h-4 text-slate-500 group-hover:text-slate-300 shrink-0" />}
        </div>
      </div>
    </aside>
  );
}
