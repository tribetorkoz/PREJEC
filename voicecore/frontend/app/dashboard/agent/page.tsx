'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Bot, Save, Play, Globe, Clock } from 'lucide-react';

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'ar', name: 'Arabic' },
  { code: 'fr', name: 'French' },
  { code: 'es', name: 'Spanish' },
  { code: 'auto', name: 'Auto-detect' },
];

const VOICES = [
  { id: 'eleven_multilingual_v2', name: 'Rachel (Multilingual)' },
  { id: 'eleven_monolingual_v1', name: 'Adam (English)' },
  { id: 'pneumatter', name: 'Samuel' },
];

export default function AgentPage() {
  const [loading, setLoading] = useState(false);
  const [agent, setAgent] = useState({
    name: 'Voice Agent',
    language: 'en',
    voice_id: 'eleven_multilingual_v2',
    system_prompt: 'You are a professional voice assistant for our company.',
    is_active: true,
  });

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.agents.update(1, agent);
      alert('Agent settings saved successfully!');
    } catch (error) {
      console.error('Failed to save agent:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Agent Configuration</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
          <Play className="w-4 h-4" />
          Test Agent
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Bot className="w-6 h-6 text-amber-500" />
            <h3 className="text-lg font-semibold text-white">Basic Settings</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Agent Name</label>
              <input
                type="text"
                value={agent.name}
                onChange={(e) => setAgent({ ...agent, name: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                <Globe className="w-4 h-4 inline mr-2" />
                Language
              </label>
              <select
                value={agent.language}
                onChange={(e) => setAgent({ ...agent, language: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>{lang.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Voice</label>
              <select
                value={agent.voice_id}
                onChange={(e) => setAgent({ ...agent, voice_id: e.target.value })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              >
                {VOICES.map((voice) => (
                  <option key={voice.id} value={voice.id}>{voice.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Status</label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setAgent({ ...agent, is_active: !agent.is_active })}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    agent.is_active 
                      ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                      : 'bg-red-500/10 text-red-500 border border-red-500/20'
                  }`}
                >
                  {agent.is_active ? 'Online' : 'Offline'}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Clock className="w-6 h-6 text-amber-500" />
            <h3 className="text-lg font-semibold text-white">System Prompt</h3>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-400 mb-2">
              Custom instructions for your AI agent
            </label>
            <textarea
              value={agent.system_prompt}
              onChange={(e) => setAgent({ ...agent, system_prompt: e.target.value })}
              rows={10}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white resize-none"
              placeholder="You are a professional voice assistant..."
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-600 disabled:opacity-50"
        >
          <Save className="w-5 h-5" />
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}
