import { Video, MessageSquare, Phone } from 'lucide-react';

const INTEGRATIONS = [
  { name: 'Zoom', icon: Video, status: 'Active', description: 'Automatic recording & transcription' },
  { name: 'Google Meet', icon: Phone, status: 'Coming Soon', description: 'Browser extension integration' },
  { name: 'Microsoft Teams', icon: MessageSquare, status: 'Coming Soon', description: 'Enterprise bot integration' },
];

export default function IntegrationsPage() {
  return (
    <div className="p-8 text-slate-200">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold uppercase mb-2">Integrations</h1>
        <p className="text-slate-400">Connect your meeting platforms for seamless intelligence gathering.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {INTEGRATIONS.map((tool) => (
          <div key={tool.name} className="bg-slate-900 border border-slate-800 p-6 group hover:border-neon-yellow transition-all">
            <div className="flex items-center justify-between mb-6">
              <div className="p-3 bg-slate-800 rounded-none group-hover:bg-neon-yellow group-hover:text-black transition-colors">
                <tool.icon className="w-8 h-8" />
              </div>
              <span className={`text-[10px] uppercase font-mono px-2 py-1 border ${
                tool.status === 'Active' 
                  ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/5' 
                  : 'border-slate-700 text-slate-500'
              }`}>
                {tool.status}
              </span>
            </div>
            
            <h3 className="text-xl font-bold mb-2">{tool.name}</h3>
            <p className="text-sm text-slate-400 mb-6 min-h-[40px]">{tool.description}</p>
            
            <button 
              disabled={tool.status !== 'Active'}
              className={`w-full py-3 text-xs font-mono uppercase tracking-widest border transition-colors ${
                tool.status === 'Active'
                  ? 'border-neon-yellow text-neon-yellow hover:bg-neon-yellow hover:text-black'
                  : 'border-slate-800 text-slate-600 cursor-not-allowed'
              }`}
            >
              {tool.status === 'Active' ? 'Configure' : 'Notify Me'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

