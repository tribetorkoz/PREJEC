'use client';

import { useEffect, useState } from 'react';
import { Zap, CheckCircle, XCircle, RefreshCw, ArrowUp, ArrowDown } from 'lucide-react';

export default function ProvidersPage() {
  const [providers, setProviders] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/admin/providers', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setProviders(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const testProvider = async (providerName: string) => {
    try {
      const token = localStorage.getItem('admin_token');
      await fetch(`/api/admin/providers/${providerName}/test`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert(`Test initiated for ${providerName}`);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Service Providers</h2>
        <button 
          onClick={fetchProviders}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 rounded-lg hover:bg-amber-600"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* STT Providers */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Speech-to-Text (STT)
        </h3>
        <div className="space-y-3">
          {providers?.stt?.map((provider: any) => (
            <div key={provider.name} className="flex items-center justify-between bg-zinc-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                {provider.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : provider.status === 'degraded' ? (
                  <XCircle className="w-5 h-5 text-yellow-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-white capitalize">{provider.name}</p>
                  <p className="text-sm text-zinc-400">Priority: {provider.priority}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Latency</p>
                  <p className="font-medium text-white">{provider.latency_ms}ms</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Success Rate</p>
                  <p className="font-medium text-green-500">{provider.success_rate}%</p>
                </div>
                <button
                  onClick={() => testProvider(provider.name)}
                  className="px-3 py-1.5 text-sm bg-zinc-700 text-white rounded hover:bg-zinc-600"
                >
                  Test
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* LLM Providers */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Language Models (LLM)
        </h3>
        <div className="space-y-3">
          {providers?.llm?.map((provider: any) => (
            <div key={provider.name} className="flex items-center justify-between bg-zinc-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                {provider.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-white capitalize">{provider.name}</p>
                  <p className="text-sm text-zinc-400">{provider.model}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Latency</p>
                  <p className="font-medium text-white">{provider.latency_ms}ms</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Success Rate</p>
                  <p className="font-medium text-green-500">{provider.success_rate}%</p>
                </div>
                <button
                  onClick={() => testProvider(provider.name)}
                  className="px-3 py-1.5 text-sm bg-zinc-700 text-white rounded hover:bg-zinc-600"
                >
                  Test
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* TTS Providers */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Text-to-Speech (TTS)
        </h3>
        <div className="space-y-3">
          {providers?.tts?.map((provider: any) => (
            <div key={provider.name} className="flex items-center justify-between bg-zinc-800 rounded-lg p-4">
              <div className="flex items-center gap-4">
                {provider.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-white capitalize">{provider.name}</p>
                  <p className="text-sm text-zinc-400">Priority: {provider.priority}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Latency</p>
                  <p className="font-medium text-white">{provider.latency_ms}ms</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-zinc-400">Success Rate</p>
                  <p className="font-medium text-green-500">{provider.success_rate}%</p>
                </div>
                <button
                  onClick={() => testProvider(provider.name)}
                  className="px-3 py-1.5 text-sm bg-zinc-700 text-white rounded hover:bg-zinc-600"
                >
                  Test
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
