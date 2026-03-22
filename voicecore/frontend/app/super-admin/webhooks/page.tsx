'use client';

import { useEffect, useState } from 'react';
import { 
  Webhook, Plus, Trash2, Edit, Bell, RefreshCw, 
  CheckCircle, XCircle, Copy, Zap
} from 'lucide-react';

interface WebhookEndpoint {
  id: string;
  name: string;
  url: string;
  events: string[];
  active: boolean;
  created_at: string;
  last_triggered?: string;
  success_rate: number;
}

const AVAILABLE_EVENTS = [
  'call.completed',
  'call.failed',
  'call.sentiment_angry',
  'call.missed',
  'appointment.created',
  'appointment.updated',
  'appointment.cancelled',
  'customer.new',
  'payment.received',
  'payment.failed',
];

const DEFAULT_WEBHOOKS: WebhookEndpoint[] = [
  {
    id: '1',
    name: 'Slack Notifications',
    url: 'https://hooks.slack.com/services/xxx',
    events: ['call.sentiment_angry', 'call.missed'],
    active: true,
    created_at: '2024-03-01T00:00:00Z',
    last_triggered: '2024-03-15T10:30:00Z',
    success_rate: 99.8
  },
  {
    id: '2',
    name: 'CRM Integration',
    url: 'https://api.crm.example.com/webhooks',
    events: ['call.completed', 'customer.new', 'appointment.created'],
    active: true,
    created_at: '2024-02-15T00:00:00Z',
    last_triggered: '2024-03-15T11:00:00Z',
    success_rate: 99.5
  },
  {
    id: '3',
    name: 'Analytics Pipeline',
    url: 'https://analytics.internal.com/events',
    events: ['call.completed', 'call.failed'],
    active: false,
    created_at: '2024-01-20T00:00:00Z',
    success_rate: 98.2
  }
];

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<WebhookEndpoint[]>(DEFAULT_WEBHOOKS);
  const [showModal, setShowModal] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState<WebhookEndpoint | null>(null);
  const [testingWebhook, setTestingWebhook] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [] as string[],
  });

  const handleCreate = () => {
    setFormData({ name: '', url: '', events: [] });
    setEditingWebhook(null);
    setShowModal(true);
  };

  const handleEdit = (webhook: WebhookEndpoint) => {
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events,
    });
    setEditingWebhook(webhook);
    setShowModal(true);
  };

  const handleSave = () => {
    if (editingWebhook) {
      setWebhooks(webhooks.map(w => 
        w.id === editingWebhook.id 
          ? { ...w, ...formData }
          : w
      ));
    } else {
      setWebhooks([...webhooks, {
        id: Date.now().toString(),
        ...formData,
        active: true,
        created_at: new Date().toISOString(),
        success_rate: 100
      }]);
    }
    setShowModal(false);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this webhook?')) {
      setWebhooks(webhooks.filter(w => w.id !== id));
    }
  };

  const toggleWebhook = (id: string) => {
    setWebhooks(webhooks.map(w => 
      w.id === id ? { ...w, active: !w.active } : w
    ));
  };

  const testWebhook = async (webhook: WebhookEndpoint) => {
    setTestingWebhook(webhook.id);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setTestingWebhook(null);
    alert(`Test payload sent to ${webhook.url}`);
  };

  const copyWebhookURL = (url: string) => {
    navigator.clipboard.writeText(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Webhooks</h2>
          <p className="text-zinc-400 mt-1">Manage outbound webhook endpoints</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
        >
          <Plus className="w-4 h-4" />
          Add Webhook
        </button>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Endpoint</th>
              <th className="text-left p-4 text-zinc-400 font-medium">URL</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Events</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Status</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Success Rate</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {webhooks.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-zinc-500">
                  No webhooks configured. Click "Add Webhook" to create one.
                </td>
              </tr>
            ) : (
              webhooks.map((webhook) => (
                <tr key={webhook.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${webhook.active ? 'bg-green-500' : 'bg-zinc-600'}`}></div>
                      <span className="text-white font-medium">{webhook.name}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <code className="text-zinc-400 text-sm bg-zinc-800 px-2 py-1 rounded max-w-[200px] truncate">
                        {webhook.url}
                      </code>
                      <button
                        onClick={() => copyWebhookURL(webhook.url)}
                        className="p-1 text-zinc-500 hover:text-white"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {webhook.events.slice(0, 2).map(event => (
                        <span key={event} className="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-xs rounded">
                          {event}
                        </span>
                      ))}
                      {webhook.events.length > 2 && (
                        <span className="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-xs rounded">
                          +{webhook.events.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => toggleWebhook(webhook.id)}
                      className={`px-3 py-1 rounded text-sm font-medium ${
                        webhook.active 
                          ? 'bg-green-500/10 text-green-500' 
                          : 'bg-zinc-800 text-zinc-400'
                      }`}
                    >
                      {webhook.active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            webhook.success_rate >= 99 ? 'bg-green-500' :
                            webhook.success_rate >= 95 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${webhook.success_rate}%` }}
                        ></div>
                      </div>
                      <span className="text-white text-sm">{webhook.success_rate}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => testWebhook(webhook)}
                        disabled={testingWebhook === webhook.id}
                        className="p-2 text-zinc-400 hover:text-amber-500 hover:bg-zinc-800 rounded"
                        title="Send test payload"
                      >
                        {testingWebhook === webhook.id ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Zap className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleEdit(webhook)}
                        className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(webhook.id)}
                        className="p-2 text-zinc-400 hover:text-red-500 hover:bg-zinc-800 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold text-white mb-6">
              {editingWebhook ? 'Edit Webhook' : 'Create Webhook'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="My Webhook"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">URL</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Events</label>
                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                  {AVAILABLE_EVENTS.map(event => (
                    <label key={event} className="flex items-center gap-2 bg-zinc-800 rounded-lg px-3 py-2 cursor-pointer hover:bg-zinc-700">
                      <input
                        type="checkbox"
                        checked={formData.events.includes(event)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({ ...formData, events: [...formData.events, event] });
                          } else {
                            setFormData({ ...formData, events: formData.events.filter(e => e !== event) });
                          }
                        }}
                        className="rounded border-zinc-600"
                      />
                      <span className="text-zinc-300 text-sm">{event}</span>
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
                {editingWebhook ? 'Save Changes' : 'Create Webhook'}
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
