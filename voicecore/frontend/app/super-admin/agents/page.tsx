'use client';

import { useEffect, useState } from 'react';
import { adminAgents, Agent } from '@/lib/admin-api';
import { Search, Edit, Power, Globe, MessageSquare } from 'lucide-react';

const VOICE_OPTIONS = [
  { id: 'eleven_multilingual_v2', name: 'Eleven Multilingual v2' },
  { id: 'eleven_monolingual_v1', name: 'Eleven English v1' },
  { id: 'pneumatter', name: 'Pneumatter' },
];

const LANGUAGE_OPTIONS = [
  { id: 'en', name: 'English' },
  { id: 'ar', name: 'Arabic' },
  { id: 'fr', name: 'French' },
  { id: 'es', name: 'Spanish' },
  { id: 'auto', name: 'Auto-detect' },
];

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const result = await adminAgents.getAll();
      setAgents(result.agents);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!editingAgent) return;
    try {
      await adminAgents.update(editingAgent.id, {
        name: editingAgent.name,
        language: editingAgent.language,
        voice_id: editingAgent.voice_id,
        system_prompt: editingAgent.system_prompt,
        is_active: editingAgent.is_active,
      });
      setEditingAgent(null);
      loadAgents();
    } catch (error) {
      console.error('Failed to update agent:', error);
    }
  };

  const toggleAgent = async (agent: Agent) => {
    try {
      await adminAgents.update(agent.id, { is_active: !agent.is_active });
      loadAgents();
    } catch (error) {
      console.error('Failed to toggle agent:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Agent Control Center</h2>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search agents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {loading ? (
          <div className="col-span-2 text-center py-8 text-zinc-500">Loading...</div>
        ) : agents.length === 0 ? (
          <div className="col-span-2 text-center py-8 text-zinc-500">No agents found</div>
        ) : (
          agents.filter(a => a.name.toLowerCase().includes(search.toLowerCase()) || a.company_name.toLowerCase().includes(search.toLowerCase())).map((agent) => (
            <div key={agent.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                  <p className="text-zinc-400 text-sm">{agent.company_name}</p>
                </div>
                <button
                  onClick={() => toggleAgent(agent)}
                  className={`p-2 rounded-lg ${agent.is_active ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}
                >
                  <Power className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Language</span>
                  <span className="text-white">{LANGUAGE_OPTIONS.find(l => l.id === agent.language)?.name || agent.language}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Voice</span>
                  <span className="text-white">{VOICE_OPTIONS.find(v => v.id === agent.voice_id)?.name || agent.voice_id}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Calls Today</span>
                  <span className="text-white">{agent.calls_today}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Status</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${agent.is_active ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                    {agent.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <button
                onClick={() => setEditingAgent(agent)}
                className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700"
              >
                <Edit className="w-4 h-4" />
                Edit Agent
              </button>
            </div>
          ))
        )}
      </div>

      {editingAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-white mb-6">Edit Agent: {editingAgent.name}</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Agent Name</label>
                <input
                  type="text"
                  value={editingAgent.name}
                  onChange={(e) => setEditingAgent({ ...editingAgent, name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Language</label>
                <select
                  value={editingAgent.language}
                  onChange={(e) => setEditingAgent({ ...editingAgent, language: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                >
                  {LANGUAGE_OPTIONS.map((lang) => (
                    <option key={lang.id} value={lang.id}>{lang.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Voice</label>
                <select
                  value={editingAgent.voice_id || ''}
                  onChange={(e) => setEditingAgent({ ...editingAgent, voice_id: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                >
                  {VOICE_OPTIONS.map((voice) => (
                    <option key={voice.id} value={voice.id}>{voice.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">System Prompt</label>
                <textarea
                  value={editingAgent.system_prompt || ''}
                  onChange={(e) => setEditingAgent({ ...editingAgent, system_prompt: e.target.value })}
                  rows={6}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white resize-none"
                  placeholder="You are a professional voice assistant..."
                />
              </div>

              <div className="flex items-center gap-4 pt-4">
                <button
                  onClick={handleUpdate}
                  className="flex-1 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => setEditingAgent(null)}
                  className="flex-1 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
