'use client';

import React from 'react';
import { Bot, Brain, Sparkles, Activity } from 'lucide-react';

export default function DigitalTwinsPage() {
  const features = [
    {
      icon: Bot,
      title: "Digital Clone Creation",
      description: "Create an AI avatar that mimics your voice, tone, and meeting style to attend meetings on your behalf."
    },
    {
      icon: Brain,
      title: "Knowledge Synthesis",
      description: "Your twin learns from your past meetings, emails, and documents to make informed decisions and provide relevant input."
    },
    {
      icon: Activity,
      title: "Active Participation",
      description: "Not just a recorder - your twin can ask questions, provide updates, and engage in discussions based on your guidelines."
    }
  ];

  return (
    <div className="h-full flex flex-col p-8 overflow-y-auto custom-scrollbar">
      <div className="max-w-5xl mx-auto w-full space-y-12">
        
        {/* Hero Section */}
        <div className="text-center space-y-6 py-12">
          <div className="inline-flex items-center justify-center p-4 bg-slate-900 rounded-full border border-neon-yellow/20 shadow-[0_0_15px_rgba(204,255,0,0.1)] mb-4">
            <Bot className="w-16 h-16 text-neon-yellow" />
          </div>
          <h1 className="text-4xl md:text-5xl font-display font-bold uppercase tracking-wider text-white">
            Digital <span className="text-neon-yellow">Twins</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto font-light">
            Scale your presence. Deploy an AI counterpart to attend concurrent meetings, gather insights, and represent your voice when you can't be there.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div key={idx} className="group p-6 bg-slate-900/50 border border-slate-800 hover:border-neon-yellow/50 transition-all duration-300 rounded-xl relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-neon-yellow/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <feature.icon className="w-8 h-8 text-neon-yellow mb-4" />
              <h3 className="text-lg font-bold text-white mb-2 font-display tracking-wide">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Coming Soon / CTA */}
        <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-800 p-8 md:p-12 overflow-hidden">
          <div className="absolute top-0 right-0 p-32 bg-neon-yellow/5 blur-3xl rounded-full -translate-y-1/2 translate-x-1/3" />
          
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 text-neon-yellow font-mono text-xs uppercase tracking-widest">
                <Sparkles className="w-3 h-3" />
                Coming Soon
              </div>
              <h2 className="text-2xl md:text-3xl font-display font-bold text-white">
                Clone Yourself. <br />
                <span className="text-slate-500">Be Everywhere at Once.</span>
              </h2>
              <p className="text-slate-400 max-w-md">
                Join the waitlist to be among the first to deploy your personal AI representative.
              </p>
            </div>

            <div className="flex flex-col gap-3 min-w-[300px]">
              <input 
                type="email" 
                placeholder="Enter your work email" 
                className="w-full bg-slate-950 border border-slate-800 text-slate-200 px-4 py-3 focus:outline-none focus:border-neon-yellow/50 transition-colors placeholder:text-slate-600 text-sm"
              />
              <button className="w-full bg-neon-yellow text-black font-bold uppercase tracking-wider py-3 hover:bg-[#b3e600] transition-colors text-sm">
                Join Waitlist
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

