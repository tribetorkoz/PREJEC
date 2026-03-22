'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Phone, Mic, ArrowRight, Loader2, Play, Pause, X, CheckCircle } from 'lucide-react';

interface Industry {
  id: string;
  name: string;
  icon: string;
  description: string;
  agent_name: string;
}

interface DemoSession {
  session_token: string;
  websocket_url: string;
  agent_config: {
    name: string;
    voice_id: string;
    greeting: string;
  };
}

export default function DemoPage() {
  const [selectedIndustry, setSelectedIndustry] = useState('dental');
  const [demoType, setDemoType] = useState<'browser' | 'phone' | null>(null);
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [session, setSession] = useState<DemoSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([
    { id: 'dental', name: 'Dental Practice', icon: '🦷', description: 'Appointments, insurance, emergency', agent_name: 'Sarah' },
    { id: 'legal', name: 'Legal Services', icon: '⚖️', description: 'Case intake, consultations', agent_name: 'Alex' },
    { id: 'realty', name: 'Real Estate', icon: '🏠', description: 'Showings, buyer qualification', agent_name: 'Jessica' },
    { id: 'general', name: 'General Business', icon: '📱', description: 'Appointments, information', agent_name: 'Max' },
  ]);

  const startBrowserDemo = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/public/demo/browser-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry: selectedIndustry }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSession(data);
        setDemoType('browser');
        setIsConnected(true);
        setTranscript([data.agent_config.greeting]);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start demo');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const startPhoneDemo = async () => {
    if (!phone) {
      setError('Please enter your phone number');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/public/demo/phone-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, industry: selectedIndustry }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setDemoType('phone');
        setIsConnected(true);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start demo call');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const endDemo = () => {
    setIsConnected(false);
    setDemoType(null);
    setSession(null);
    setTranscript([]);
  };

  const currentIndustry = industries.find((i) => i.id === selectedIndustry);

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
                <Phone className="w-6 h-6 text-zinc-950" />
              </div>
              <span className="text-xl font-bold text-white">VoiceCore</span>
            </Link>
            <Link
              href="/signup"
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-4 py-2 rounded-lg transition"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Live Demo
          </h1>
          <p className="text-xl text-zinc-400">
            Hear your AI receptionist before you sign up
          </p>
        </div>

        {/* Industry Selection */}
        {!isConnected && (
          <div className="mb-8">
            <h2 className="text-lg font-medium text-white mb-4 text-center">Select your industry:</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {industries.map((ind) => (
                <button
                  key={ind.id}
                  onClick={() => setSelectedIndustry(ind.id)}
                  className={`p-4 rounded-xl border transition ${
                    selectedIndustry === ind.id
                      ? 'border-amber-500 bg-amber-500/10 text-white'
                      : 'border-zinc-700 bg-zinc-900 text-zinc-400 hover:border-zinc-600'
                  }`}
                >
                  <div className="text-3xl mb-2">{ind.icon}</div>
                  <div className="font-medium">{ind.name}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Demo Type Selection */}
        {!isConnected && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Browser Demo */}
            <button
              onClick={startBrowserDemo}
              disabled={isLoading}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-left hover:border-zinc-700 transition"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center">
                  <Mic className="w-8 h-8 text-amber-500" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Try in Browser</h3>
                  <p className="text-zinc-500">No app needed</p>
                </div>
              </div>
              <p className="text-zinc-400 mb-4">
                Start a live conversation right here. Speak with {currentIndustry?.agent_name}, your AI receptionist.
              </p>
              {isLoading && demoType === 'browser' ? (
                <div className="flex items-center gap-2 text-amber-500">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Connecting...
                </div>
              ) : (
                <div className="flex items-center gap-2 text-amber-500 font-medium">
                  <Play className="w-5 h-5" />
                  Start Now
                </div>
              )}
            </button>

            {/* Phone Demo */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center">
                  <Phone className="w-8 h-8 text-amber-500" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Call me now</h3>
                  <p className="text-zinc-500">We call your phone</p>
                </div>
              </div>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 mb-4"
              />
              <button
                onClick={startPhoneDemo}
                disabled={isLoading}
                className="w-full bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-zinc-950 font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
              >
                {isLoading && demoType === 'phone' ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Calling...
                  </>
                ) : (
                  <>
                    <Phone className="w-5 h-5" />
                    Call My Phone
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-8">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Browser Demo Connected */}
        {isConnected && demoType === 'browser' && session && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                <span className="text-green-500 font-medium">Connected</span>
              </div>
              <button
                onClick={endDemo}
                className="bg-red-500 hover:bg-red-400 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition"
              >
                <X className="w-4 h-4" />
                End Demo
              </button>
            </div>

            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-white mb-2">
                {currentIndustry?.icon} {session.agent_config.name}
              </h3>
              <p className="text-zinc-400">{currentIndustry?.name} Demo</p>
            </div>

            {/* Waveform Animation */}
            <div className="flex items-center justify-center gap-1 h-16 mb-6">
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 bg-amber-500 rounded-full"
                  style={{
                    height: `${20 + Math.sin(i * 0.5 + Date.now() / 200) * 30}%`,
                    animation: 'wave 1s ease-in-out infinite',
                  }}
                />
              ))}
            </div>

            <p className="text-center text-zinc-400 mb-6">
              "Go ahead, speak now..."
            </p>

            {/* Transcript */}
            <div className="bg-zinc-800 rounded-lg p-4 max-h-48 overflow-y-auto">
              {transcript.map((line, i) => (
                <div key={i} className="text-zinc-300 mb-2">
                  <span className="text-amber-500 font-medium">{session.agent_config.name}:</span> {line}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Phone Demo Connected */}
        {isConnected && demoType === 'phone' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Phone className="w-10 h-10 text-green-500 animate-pulse" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Calling {phone}...
            </h3>
            <p className="text-zinc-400 mb-6">
              Answer your phone to speak with {currentIndustry?.agent_name}
            </p>
            <button
              onClick={endDemo}
              className="bg-zinc-700 hover:bg-zinc-600 text-white px-6 py-2 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        )}

        {/* CTA after demo */}
        {!isConnected && (
          <div className="text-center mt-12 pt-8 border-t border-zinc-800">
            <h3 className="text-xl font-semibold text-white mb-2">
              Liked what you heard?
            </h3>
            <p className="text-zinc-400 mb-6">
              Start your free 14-day trial — no credit card required
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-6 py-3 rounded-lg transition"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        )}
      </main>

      <style jsx global>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(0.5); }
        }
      `}</style>
    </div>
  );
}
