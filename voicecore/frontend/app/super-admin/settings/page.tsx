'use client';

import { useEffect, useState } from 'react';
import { adminSettings, SettingsData, FeatureFlag } from '@/lib/admin-api';
import { Key, Save, Eye, EyeOff, ToggleLeft, ToggleRight, Bell, Database, Download } from 'lucide-react';

export default function SettingsPage() {
  const [data, setData] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [keyValue, setKeyValue] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const result = await adminSettings.getData();
      setData(result);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKey = async (key: string) => {
    try {
      await adminSettings.updateApiKey(key, keyValue);
      setEditingKey(null);
      setKeyValue('');
      loadSettings();
    } catch (error) {
      console.error('Failed to update API key:', error);
    }
  };

  const handleToggleFlag = async (flag: FeatureFlag) => {
    try {
      await adminSettings.updateFeatureFlag(flag.id, {
        name: flag.name,
        description: flag.description,
        is_global_enabled: !flag.is_global_enabled,
      });
      loadSettings();
    } catch (error) {
      console.error('Failed to toggle feature flag:', error);
    }
  };

  const getKeyLabel = (key: string) => {
    const labels: Record<string, string> = {
      DEEPGRAM_API_KEY: 'Deepgram API Key',
      ELEVENLABS_API_KEY: 'ElevenLabs API Key',
      ANTHROPIC_API_KEY: 'Anthropic API Key',
      TWILIO_ACCOUNT_SID: 'Twilio Account SID',
      TWILIO_AUTH_TOKEN: 'Twilio Auth Token',
      STRIPE_SECRET_KEY: 'Stripe Secret Key',
      LIVEKIT_URL: 'LiveKit URL',
    };
    return labels[key] || key;
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
      <h2 className="text-xl font-semibold text-white">System Settings</h2>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Key className="w-5 h-5" />
          API Keys Manager
        </h3>
        <p className="text-zinc-400 text-sm mb-6">
          Update API keys. All changes are logged for security.
        </p>
        
        <div className="space-y-3">
          {data?.api_keys.map((setting) => (
            <div key={setting.key} className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
              <div className="flex-1">
                <p className="text-white font-medium">{getKeyLabel(setting.key)}</p>
                <p className="text-zinc-500 text-sm font-mono">{setting.display_value}</p>
              </div>
              {editingKey === setting.key ? (
                <div className="flex items-center gap-2">
                  <input
                    type="password"
                    value={keyValue}
                    onChange={(e) => setKeyValue(e.target.value)}
                    placeholder="Enter new value"
                    className="bg-zinc-700 border border-zinc-600 rounded px-3 py-1 text-white text-sm"
                  />
                  <button
                    onClick={() => handleSaveKey(setting.key)}
                    className="p-2 bg-amber-500 text-zinc-950 rounded hover:bg-amber-600"
                  >
                    <Save className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setEditingKey(null)}
                    className="p-2 bg-zinc-700 text-white rounded hover:bg-zinc-600"
                  >
                    <EyeOff className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setEditingKey(setting.key)}
                  className="px-4 py-2 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 flex items-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  Edit
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <ToggleLeft className="w-5 h-5" />
          Feature Flags
        </h3>
        
        <div className="space-y-3">
          {data?.feature_flags.length === 0 ? (
            <p className="text-zinc-500">No feature flags configured</p>
          ) : (
            data?.feature_flags.map((flag) => (
              <div key={flag.id} className="flex items-center justify-between p-4 bg-zinc-800 rounded-lg">
                <div>
                  <p className="text-white font-medium">{flag.name}</p>
                  <p className="text-zinc-500 text-sm">{flag.description}</p>
                </div>
                <button
                  onClick={() => handleToggleFlag(flag)}
                  className={`p-2 rounded ${flag.is_global_enabled ? 'text-green-500' : 'text-zinc-500'}`}
                >
                  {flag.is_global_enabled ? (
                    <ToggleRight className="w-8 h-8" />
                  ) : (
                    <ToggleLeft className="w-8 h-8" />
                  )}
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notification Center
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-2">Target Audience</label>
            <select className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white">
              <option>All Clients</option>
              <option>Starter Plan</option>
              <option>Business Plan</option>
              <option>Enterprise Plan</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-zinc-400 mb-2">Message Type</label>
            <select className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white">
              <option>Maintenance Alert</option>
              <option>New Feature</option>
              <option>Invoice Reminder</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-zinc-400 mb-2">Message</label>
            <textarea 
              rows={4}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white resize-none"
              placeholder="Enter your message..."
            />
          </div>
          
          <button className="px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600">
            Send Notification
          </button>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          Backup & Export
        </h3>
        
        <div className="flex flex-wrap gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
            <Download className="w-4 h-4" />
            Database Backup
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
            <Download className="w-4 h-4" />
            Export Clients CSV
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
            <Download className="w-4 h-4" />
            Export Calls CSV
          </button>
        </div>
      </div>
    </div>
  );
}
