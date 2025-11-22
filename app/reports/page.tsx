'use client';

import { BarChart3, TrendingUp, PieChart, Lock } from 'lucide-react';
import { useNeoWallet } from '../context/NeoWalletContext';

export default function ReportsPage() {
  const { isConnected } = useNeoWallet();

  if (!isConnected) {
    return (
      <div className="p-8 text-slate-200 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800 animate-pulse mx-auto">
            <Lock className="w-10 h-10 text-neon-yellow" />
          </div>
          <h1 className="text-3xl font-display font-bold uppercase mb-3">Access Restricted</h1>
          <p className="text-slate-400 max-w-md">
             Connect your Neo wallet to view intelligence reports.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 text-slate-200 h-full flex items-center justify-center">
      <div className="text-center max-w-lg">
        <div className="w-24 h-24 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-6 border border-slate-800">
          <TrendingUp className="w-10 h-10 text-neon-yellow" />
        </div>
        <h1 className="text-3xl font-display font-bold uppercase mb-4">AI Intelligence Reports</h1>
        <p className="text-slate-400 mb-8">
          Deep analytics on meeting sentiment, speaker effectiveness, and action item completion rates are processing.
        </p>
        <div className="grid grid-cols-3 gap-4 opacity-50">
          <div className="h-32 bg-slate-900 border border-slate-800 animate-pulse"></div>
          <div className="h-32 bg-slate-900 border border-slate-800 animate-pulse delay-100"></div>
          <div className="h-32 bg-slate-900 border border-slate-800 animate-pulse delay-200"></div>
        </div>
      </div>
    </div>
  );
}
