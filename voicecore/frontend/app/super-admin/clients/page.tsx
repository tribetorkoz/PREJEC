'use client';

import { useEffect, useState } from 'react';
import { adminClients, Client } from '@/lib/admin-api';
import { Search, Plus, MoreVertical, Edit, Pause, Trash2, Mail, Eye } from 'lucide-react';

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [plan, setPlan] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadClients();
  }, [search, plan, page]);

  const loadClients = async () => {
    try {
      const result = await adminClients.getAll(search || undefined, plan || undefined, page);
      setClients(result.clients);
      setTotalPages(result.pages);
    } catch (error) {
      console.error('Failed to load clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspend = async (id: number) => {
    if (!confirm('Are you sure you want to suspend this client?')) return;
    try {
      await adminClients.suspend(id);
      loadClients();
    } catch (error) {
      console.error('Failed to suspend client:', error);
    }
  };

  const handleDelete = async (id: number) => {
    const companyName = prompt('Type DELETE to confirm:');
    if (companyName !== 'DELETE') return;
    try {
      await adminClients.delete(id);
      loadClients();
    } catch (error) {
      console.error('Failed to delete client:', error);
    }
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Client Management</h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600"
        >
          <Plus className="w-4 h-4" />
          Add Client
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <select
          value={plan}
          onChange={(e) => setPlan(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Plans</option>
          <option value="starter">Starter</option>
          <option value="business">Business</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Company</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Plan</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Status</th>
              <th className="text-left p-4 text-zinc-400 font-medium">MRR</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Calls</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Joined</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-zinc-500">Loading...</td>
              </tr>
            ) : clients.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-zinc-500">No clients found</td>
              </tr>
            ) : (
              clients.map((client) => (
                <tr key={client.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                  <td className="p-4">
                    <div>
                      <p className="text-white font-medium">{client.name}</p>
                      <p className="text-zinc-500 text-sm">{client.email}</p>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-zinc-800 text-zinc-300 text-sm rounded capitalize">
                      {client.plan}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-sm rounded ${
                      client.status === 'active' 
                        ? 'bg-green-500/10 text-green-500' 
                        : 'bg-red-500/10 text-red-500'
                    }`}>
                      {client.status}
                    </span>
                  </td>
                  <td className="p-4 text-white">{formatCurrency(client.mrr)}</td>
                  <td className="p-4 text-white">{client.calls_count}</td>
                  <td className="p-4 text-zinc-400">
                    {client.created_at ? new Date(client.created_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <button className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleSuspend(client.id)}
                        className="p-2 text-zinc-400 hover:text-yellow-500 hover:bg-zinc-800 rounded"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(client.id)}
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

      <div className="flex items-center justify-between">
        <p className="text-zinc-400">Page {page} of {totalPages}</p>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-zinc-800 text-white rounded-lg disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 bg-zinc-800 text-white rounded-lg disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
