'use client';

import { useEffect, useState } from 'react';
import { Globe, Plus, Edit, Trash2, CheckCircle, XCircle, DollarSign, Phone } from 'lucide-react';

interface Vertical {
  id: string;
  name: string;
  domain: string;
  price_monthly: number;
  companies_count: number;
  calls_count: number;
  is_active: boolean;
}

const DEFAULT_VERTICALS: Vertical[] = [
  { id: 'general', name: 'VoiceCore', domain: 'voicecore.ai', price_monthly: 299, companies_count: 120, calls_count: 35000, is_active: true },
  { id: 'dental', name: 'DentalVoice', domain: 'dentalvoice.ai', price_monthly: 399, companies_count: 85, calls_count: 22000, is_active: true },
  { id: 'legal', name: 'LegalVoice', domain: 'legalvoice.ai', price_monthly: 599, companies_count: 45, calls_count: 12000, is_active: true },
  { id: 'realty', name: 'RealtorVoice', domain: 'realtyvoice.ai', price_monthly: 299, companies_count: 65, calls_count: 18000, is_active: true },
  { id: 'medical', name: 'MediVoice', domain: 'medivioce.ai', price_monthly: 499, companies_count: 35, calls_count: 9500, is_active: true },
  { id: 'auto', name: 'AutoVoice', domain: 'autovoice.ai', price_monthly: 349, companies_count: 28, calls_count: 7500, is_active: true },
];

export default function VerticalsPage() {
  const [verticals, setVerticals] = useState<Vertical[]>(DEFAULT_VERTICALS);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingVertical, setEditingVertical] = useState<Vertical | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    price_monthly: 299,
    is_active: true,
  });

  useEffect(() => {
    fetchVerticals();
  }, []);

  const fetchVerticals = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/admin/verticals', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.verticals) {
        setVerticals(data.verticals);
      }
    } catch (error) {
      console.error('Error fetching verticals:', error);
    }
    setLoading(false);
  };

  const handleCreate = () => {
    setFormData({ name: '', domain: '', price_monthly: 299, is_active: true });
    setEditingVertical(null);
    setShowModal(true);
  };

  const handleEdit = (vertical: Vertical) => {
    setFormData({
      name: vertical.name,
      domain: vertical.domain,
      price_monthly: vertical.price_monthly,
      is_active: vertical.is_active,
    });
    setEditingVertical(vertical);
    setShowModal(true);
  };

  const handleSave = () => {
    if (editingVertical) {
      setVerticals(verticals.map(v => 
        v.id === editingVertical.id 
          ? { ...v, ...formData }
          : v
      ));
    } else {
      setVerticals([...verticals, {
        id: formData.name.toLowerCase().replace(/\s+/g, ''),
        ...formData,
        companies_count: 0,
        calls_count: 0,
      }]);
    }
    setShowModal(false);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this vertical?')) {
      setVerticals(verticals.filter(v => v.id !== id));
    }
  };

  const toggleVertical = (id: string) => {
    setVerticals(verticals.map(v => 
      v.id === id ? { ...v, is_active: !v.is_active } : v
    ));
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  const totalMRR = verticals.reduce((sum, v) => sum + (v.price_monthly * v.companies_count), 0);
  const totalCalls = verticals.reduce((sum, v) => sum + v.calls_count, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Industry Verticals</h2>
          <p className="text-zinc-400 mt-1">Create and manage branded AI receptionist verticals</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 rounded-lg hover:bg-amber-600"
        >
          <Plus className="w-4 h-4" />
          Add Vertical
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Globe className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Total Verticals</p>
              <p className="text-2xl font-bold text-white">{verticals.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Vertical Revenue</p>
              <p className="text-2xl font-bold text-white">{formatCurrency(totalMRR)}</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500/10 rounded-lg flex items-center justify-center">
              <Phone className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Total Calls</p>
              <p className="text-2xl font-bold text-white">{totalCalls.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {verticals.map((vertical) => (
          <div key={vertical.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-amber-500/10 rounded-lg flex items-center justify-center">
                  <Globe className="w-6 h-6 text-amber-500" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{vertical.name}</h3>
                  <p className="text-sm text-zinc-400">{vertical.domain}</p>
                </div>
              </div>
              <button
                onClick={() => toggleVertical(vertical.id)}
                className={`p-1 rounded ${vertical.is_active ? 'text-green-500' : 'text-zinc-500'}`}
              >
                {vertical.is_active ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
              </button>
            </div>

            <div className="pt-4 border-t border-zinc-800">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-white">${vertical.price_monthly}</p>
                  <p className="text-xs text-zinc-400">/month</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{vertical.companies_count}</p>
                  <p className="text-xs text-zinc-400">Companies</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{(vertical.calls_count / 1000).toFixed(0)}k</p>
                  <p className="text-xs text-zinc-400">Calls</p>
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleEdit(vertical)}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={() => handleDelete(vertical.id)}
                className="px-3 py-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500/20"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold text-white mb-6">
              {editingVertical ? 'Edit Vertical' : 'Add Vertical'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Vertical Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="DentalVoice"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Domain</label>
                <input
                  type="text"
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="dentalvoice.ai"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Monthly Price ($)</label>
                <input
                  type="number"
                  value={formData.price_monthly}
                  onChange={(e) => setFormData({ ...formData, price_monthly: Number(e.target.value) })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                />
              </div>

              <label className="flex items-center gap-3 bg-zinc-800 rounded-lg px-4 py-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded border-zinc-600"
                />
                <span className="text-white">Active</span>
              </label>
            </div>

            <div className="flex items-center gap-4 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
              >
                {editingVertical ? 'Save Changes' : 'Create Vertical'}
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
