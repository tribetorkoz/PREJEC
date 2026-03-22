'use client';

import { useEffect, useState } from 'react';
import { 
  Key, Plus, Trash2, Eye, EyeOff, Copy, 
  RefreshCw, Shield, AlertTriangle, CheckCircle
} from 'lucide-react';

interface APIKey {
  id: string;
  name: string;
  key_preview: string;
  full_key?: string;
  created_at: string;
  last_used?: string;
  permissions: string[];
  active: boolean;
  env_var: string;
}

const API_KEYS: APIKey[] = [
  {
    id: '1',
    name: 'Production Deepgram',
    key_preview: '••••••••••••••••a1b2',
    created_at: '2024-01-15T00:00:00Z',
    last_used: '2024-03-15T10:00:00Z',
    permissions: ['stt', 'streaming'],
    active: true,
    env_var: 'DEEPGRAM_API_KEY'
  },
  {
    id: '2',
    name: 'Production Anthropic',
    key_preview: '••••••••••••••••x9y8',
    created_at: '2024-02-01T00:00:00Z',
    last_used: '2024-03-15T11:00:00Z',
    permissions: ['llm', 'streaming'],
    active: true,
    env_var: 'ANTHROPIC_API_KEY'
  },
  {
    id: '3',
    name: 'Production ElevenLabs',
    key_preview: '••••••••••••••••c3d4',
    created_at: '2024-02-15T00:00:00Z',
    last_used: '2024-03-15T09:30:00Z',
    permissions: ['tts', 'voices'],
    active: true,
    env_var: 'ELEVENLABS_API_KEY'
  },
  {
    id: '4',
    name: 'Stripe Live',
    key_preview: '••••••••••••••••s5t6',
    created_at: '2024-01-01T00:00:00Z',
    last_used: '2024-03-15T08:00:00Z',
    permissions: ['billing', 'subscriptions'],
    active: true,
    env_var: 'STRIPE_SECRET_KEY'
  },
  {
    id: '5',
    name: 'Twilio Production',
    key_preview: '••••••••••••••••u7v8',
    created_at: '2024-01-10T00:00:00Z',
    last_used: '2024-03-15T07:00:00Z',
    permissions: ['calls', 'sms'],
    active: true,
    env_var: 'TWILIO_AUTH_TOKEN'
  },
  {
    id: '6',
    name: 'SendGrid',
    key_preview: '••••••••••••••••w9x0',
    created_at: '2024-01-20T00:00:00Z',
    last_used: '2024-03-14T20:00:00Z',
    permissions: ['emails', 'templates'],
    active: true,
    env_var: 'SENDGRID_API_KEY'
  },
];

export default function APIKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>(API_KEYS);
  const [showModal, setShowModal] = useState(false);
  const [showKey, setShowKey] = useState<string | null>(null);
  const [newKeyData, setNewKeyData] = useState({
    name: '',
    env_var: '',
    permissions: [] as string[],
  });

  const PERMISSIONS = [
    { id: 'stt', name: 'Speech-to-Text' },
    { id: 'llm', name: 'Language Models' },
    { id: 'tts', name: 'Text-to-Speech' },
    { id: 'calls', name: 'Voice Calls' },
    { id: 'sms', name: 'SMS' },
    { id: 'billing', name: 'Billing' },
    { id: 'emails', name: 'Emails' },
  ];

  const handleCreate = () => {
    setNewKeyData({ name: '', env_var: '', permissions: [] });
    setShowModal(true);
  };

  const handleSave = () => {
    const fakeKey = `${newKeyData.env_var.toLowerCase().replace(/_/g, '-')}_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    setKeys([...keys, {
      id: Date.now().toString(),
      name: newKeyData.name,
      key_preview: '••••••••••••••••' + fakeKey.slice(-4),
      full_key: fakeKey,
      created_at: new Date().toISOString(),
      permissions: newKeyData.permissions,
      active: true,
      env_var: newKeyData.env_var,
    }]);
    setShowModal(false);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this API key?')) {
      setKeys(keys.filter(k => k.id !== id));
    }
  };

  const toggleKey = (id: string) => {
    setKeys(keys.map(k => 
      k.id === id ? { ...k, active: !k.active } : k
    ));
  };

  const copyKey = (key: APIKey) => {
    if (key.full_key) {
      navigator.clipboard.writeText(key.full_key);
    }
  };

  const formatDate = (date: string) => new Date(date).toLocaleDateString();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">API Keys & Secrets</h2>
          <p className="text-zinc-400 mt-1">Manage service provider credentials</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
        >
          <Plus className="w-4 h-4" />
          Add API Key
        </button>
      </div>

      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
        <Shield className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-amber-500 font-medium">Security Best Practices</p>
          <p className="text-zinc-400 text-sm mt-1">
            All API keys are encrypted at rest using AES-256. Never share API keys publicly.
          </p>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Name</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Environment Variable</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Key Preview</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Permissions</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Last Used</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Status</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                <td className="p-4">
                  <span className="text-white font-medium">{key.name}</span>
                </td>
                <td className="p-4">
                  <code className="text-zinc-400 text-sm bg-zinc-800 px-2 py-1 rounded">
                    {key.env_var}
                  </code>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <code className="text-zinc-300 font-mono">
                      {showKey === key.id ? (key.full_key || key.key_preview) : key.key_preview}
                    </code>
                    <button
                      onClick={() => setShowKey(showKey === key.id ? null : key.id)}
                      className="p-1 text-zinc-500 hover:text-white"
                    >
                      {showKey === key.id ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    {key.full_key && (
                      <button
                        onClick={() => copyKey(key)}
                        className="p-1 text-zinc-500 hover:text-white"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex flex-wrap gap-1">
                    {key.permissions.map(perm => (
                      <span key={perm} className="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-xs rounded capitalize">
                        {perm}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="p-4 text-zinc-400 text-sm">
                  {key.last_used ? formatDate(key.last_used) : 'Never'}
                </td>
                <td className="p-4">
                  <button
                    onClick={() => toggleKey(key.id)}
                    className={`px-3 py-1 rounded text-sm font-medium ${
                      key.active 
                        ? 'bg-green-500/10 text-green-500' 
                        : 'bg-zinc-800 text-zinc-400'
                    }`}
                  >
                    {key.active ? 'Active' : 'Inactive'}
                  </button>
                </td>
                <td className="p-4">
                  <button
                    onClick={() => handleDelete(key.id)}
                    className="p-2 text-zinc-400 hover:text-red-500 hover:bg-zinc-800 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold text-white mb-6">Add API Key</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Name</label>
                <input
                  type="text"
                  value={newKeyData.name}
                  onChange={(e) => setNewKeyData({ ...newKeyData, name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="My API Key"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Environment Variable Name</label>
                <input
                  type="text"
                  value={newKeyData.env_var}
                  onChange={(e) => setNewKeyData({ ...newKeyData, env_var: e.target.value.toUpperCase() })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="MY_API_KEY"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Permissions</label>
                <div className="grid grid-cols-2 gap-2">
                  {PERMISSIONS.map(perm => (
                    <label key={perm.id} className="flex items-center gap-2 bg-zinc-800 rounded-lg px-3 py-2 cursor-pointer hover:bg-zinc-700">
                      <input
                        type="checkbox"
                        checked={newKeyData.permissions.includes(perm.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewKeyData({ ...newKeyData, permissions: [...newKeyData.permissions, perm.id] });
                          } else {
                            setNewKeyData({ ...newKeyData, permissions: newKeyData.permissions.filter(p => p !== perm.id) });
                          }
                        }}
                        className="rounded border-zinc-600"
                      />
                      <span className="text-zinc-300 text-sm">{perm.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
              >
                Add Key
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
