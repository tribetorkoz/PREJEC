'use client';

import { useEffect, useState } from 'react';
import { 
  Building2, Plus, Trash2, Edit, DollarSign, 
  Users, Globe, TrendingUp, ExternalLink, Copy,
  MoreVertical
} from 'lucide-react';

interface WhiteLabelPartner {
  id: string;
  brand_name: string;
  company_name: string;
  domain: string;
  revenue_share: number;
  max_clients: number;
  current_clients: number;
  monthly_revenue: number;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
}

const PARTNERS: WhiteLabelPartner[] = [
  {
    id: '1',
    brand_name: 'DentalVoice',
    company_name: 'DentalVoice Inc.',
    domain: 'ai.dentalvoice.com',
    revenue_share: 20,
    max_clients: 100,
    current_clients: 45,
    monthly_revenue: 13455,
    status: 'active',
    created_at: '2024-01-15T00:00:00Z'
  },
  {
    id: '2',
    brand_name: 'LegalConnect',
    company_name: 'LegalConnect LLC',
    domain: 'voice.legalconnect.com',
    revenue_share: 25,
    max_clients: 50,
    current_clients: 28,
    monthly_revenue: 25182,
    status: 'active',
    created_at: '2024-02-01T00:00:00Z'
  },
  {
    id: '3',
    brand_name: 'RealtorAI',
    company_name: 'RealtorAI Corp',
    domain: 'call.realtorai.io',
    revenue_share: 20,
    max_clients: 200,
    current_clients: 112,
    monthly_revenue: 33504,
    status: 'active',
    created_at: '2024-01-20T00:00:00Z'
  },
  {
    id: '4',
    brand_name: 'MediPhone',
    company_name: 'MediPhone Health',
    domain: 'ai.mediphone.com',
    revenue_share: 30,
    max_clients: 75,
    current_clients: 12,
    monthly_revenue: 5396,
    status: 'pending',
    created_at: '2024-03-01T00:00:00Z'
  }
];

export default function WhiteLabelPage() {
  const [partners, setPartners] = useState<WhiteLabelPartner[]>(PARTNERS);
  const [showModal, setShowModal] = useState(false);
  const [editingPartner, setEditingPartner] = useState<WhiteLabelPartner | null>(null);
  const [formData, setFormData] = useState({
    brand_name: '',
    company_name: '',
    domain: '',
    revenue_share: 20,
    max_clients: 50,
  });

  const totalMRR = partners.reduce((sum, p) => sum + p.monthly_revenue, 0);
  const totalClients = partners.reduce((sum, p) => sum + p.current_clients, 0);
  const totalPayouts = partners.reduce((sum, p) => sum + (p.monthly_revenue * p.revenue_share / 100), 0);

  const handleCreate = () => {
    setFormData({ brand_name: '', company_name: '', domain: '', revenue_share: 20, max_clients: 50 });
    setEditingPartner(null);
    setShowModal(true);
  };

  const handleEdit = (partner: WhiteLabelPartner) => {
    setFormData({
      brand_name: partner.brand_name,
      company_name: partner.company_name,
      domain: partner.domain,
      revenue_share: partner.revenue_share,
      max_clients: partner.max_clients,
    });
    setEditingPartner(partner);
    setShowModal(true);
  };

  const handleSave = () => {
    if (editingPartner) {
      setPartners(partners.map(p => 
        p.id === editingPartner.id 
          ? { ...p, ...formData }
          : p
      ));
    } else {
      setPartners([...partners, {
        id: Date.now().toString(),
        ...formData,
        current_clients: 0,
        monthly_revenue: 0,
        status: 'pending',
        created_at: new Date().toISOString()
      }]);
    }
    setShowModal(false);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this partner?')) {
      setPartners(partners.filter(p => p.id !== id));
    }
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">White-Label Partners</h2>
          <p className="text-zinc-400 mt-1">Manage branded AI receptionist resellers</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
        >
          <Plus className="w-4 h-4" />
          Add Partner
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Total Partners</p>
              <p className="text-2xl font-bold text-white">{partners.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Total Clients</p>
              <p className="text-2xl font-bold text-white">{totalClients}</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-amber-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Total Revenue</p>
              <p className="text-2xl font-bold text-white">{formatCurrency(totalMRR)}</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-zinc-400 text-sm">Partner Payouts</p>
              <p className="text-2xl font-bold text-white">{formatCurrency(totalPayouts)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Partner</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Domain</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Clients</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Revenue Share</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Monthly Revenue</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Payout</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Status</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {partners.map((partner) => (
              <tr key={partner.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                <td className="p-4">
                  <div>
                    <p className="text-white font-medium">{partner.brand_name}</p>
                    <p className="text-zinc-500 text-sm">{partner.company_name}</p>
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-zinc-500" />
                    <span className="text-zinc-400 text-sm">{partner.domain}</span>
                    <a href={`https://${partner.domain}`} target="_blank" className="text-zinc-500 hover:text-white">
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-zinc-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-amber-500 rounded-full"
                        style={{ width: `${(partner.current_clients / partner.max_clients) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-white text-sm">{partner.current_clients}/{partner.max_clients}</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="text-amber-500 font-medium">{partner.revenue_share}%</span>
                </td>
                <td className="p-4">
                  <span className="text-white font-medium">{formatCurrency(partner.monthly_revenue)}</span>
                </td>
                <td className="p-4">
                  <span className="text-green-500">{formatCurrency(partner.monthly_revenue * partner.revenue_share / 100)}</span>
                </td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${
                    partner.status === 'active' ? 'bg-green-500/10 text-green-500' :
                    partner.status === 'pending' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-zinc-800 text-zinc-400'
                  }`}>
                    {partner.status}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEdit(partner)}
                      className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(partner.id)}
                      className="p-2 text-zinc-400 hover:text-red-500 hover:bg-zinc-800 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold text-white mb-6">
              {editingPartner ? 'Edit Partner' : 'Add Partner'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Brand Name</label>
                <input
                  type="text"
                  value={formData.brand_name}
                  onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="DentalVoice"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Company Name</label>
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="DentalVoice Inc."
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Domain</label>
                <input
                  type="text"
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  placeholder="ai.dentalvoice.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Revenue Share (%)</label>
                  <input
                    type="number"
                    value={formData.revenue_share}
                    onChange={(e) => setFormData({ ...formData, revenue_share: Number(e.target.value) })}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Max Clients</label>
                  <input
                    type="number"
                    value={formData.max_clients}
                    onChange={(e) => setFormData({ ...formData, max_clients: Number(e.target.value) })}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
              >
                {editingPartner ? 'Save Changes' : 'Add Partner'}
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
