'use client';

import { useEffect, useState } from 'react';
import { Search, Phone, Clock, BarChart3, Users as UsersIcon, Filter } from 'lucide-react';

interface CustomerCall {
  id: number;
  company_name: string;
  company_id: number;
  duration_seconds: number;
  sentiment: string;
  outcome: string;
  transcript?: string;
  created_at: string;
}

interface Customer {
  phone: string;
  total_calls: number;
  first_call: string;
  last_call?: string;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customerHistory, setCustomerHistory] = useState<CustomerCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadCustomers();
  }, [page]);

  const loadCustomers = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/admin/customers?page=${page}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setCustomers(data.customers || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCustomerHistory = async (phone: string) => {
    setLoadingHistory(true);
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/admin/customers/${encodeURIComponent(phone)}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setCustomerHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleCustomerClick = async (customer: Customer) => {
    setSelectedCustomer(customer);
    await loadCustomerHistory(customer.phone);
  };

  const getSentimentColor = (s: string) => {
    switch (s) {
      case 'POSITIVE': return 'bg-green-500/10 text-green-500';
      case 'NEUTRAL': return 'bg-yellow-500/10 text-yellow-500';
      case 'ANGRY': return 'bg-red-500/10 text-red-500';
      default: return 'bg-zinc-800 text-zinc-400';
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredCustomers = customers.filter(c => 
    c.phone.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Customer Intelligence</h2>
        <div className="flex items-center gap-2 text-sm text-zinc-400">
          <UsersIcon className="w-4 h-4" />
          {total} unique callers
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-zinc-800">
            <h3 className="text-white font-medium">All Callers</h3>
          </div>
          <div className="max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-zinc-500">Loading...</div>
            ) : filteredCustomers.length === 0 ? (
              <div className="p-8 text-center text-zinc-500">No customers found</div>
            ) : (
              filteredCustomers.map((customer) => (
                <div
                  key={customer.phone}
                  onClick={() => handleCustomerClick(customer)}
                  className={`p-4 border-b border-zinc-800 hover:bg-zinc-800/50 cursor-pointer ${
                    selectedCustomer?.phone === customer.phone ? 'bg-amber-500/10' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">{customer.phone}</p>
                      <p className="text-zinc-500 text-sm">
                        {customer.total_calls} calls
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-zinc-400 text-sm">
                        First: {customer.first_call ? new Date(customer.first_call).toLocaleDateString() : '-'}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="p-4 border-t border-zinc-800 flex items-center justify-between">
            <p className="text-zinc-400 text-sm">Page {page}</p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-zinc-800 text-white text-sm rounded disabled:opacity-50"
              >
                Prev
              </button>
              <button
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 bg-zinc-800 text-white text-sm rounded"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-zinc-800">
            <h3 className="text-white font-medium">
              {selectedCustomer ? `Call History: ${selectedCustomer.phone}` : 'Select a caller'}
            </h3>
          </div>
          <div className="max-h-[600px] overflow-y-auto">
            {!selectedCustomer ? (
              <div className="p-8 text-center text-zinc-500">Select a caller to view history</div>
            ) : loadingHistory ? (
              <div className="p-8 text-center text-zinc-500">Loading...</div>
            ) : customerHistory.length === 0 ? (
              <div className="p-8 text-center text-zinc-500">No calls found</div>
            ) : (
              customerHistory.map((call) => (
                <div key={call.id} className="p-4 border-b border-zinc-800">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <Phone className="w-4 h-4 text-zinc-500" />
                      <span className="text-white font-medium">{call.company_name}</span>
                    </div>
                    <span className={`px-2 py-0.5 text-xs rounded ${getSentimentColor(call.sentiment || '')}`}>
                      {call.sentiment || 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-zinc-400">
                    <span>{formatDuration(call.duration_seconds)}</span>
                    <span>{call.outcome || '-'}</span>
                    <span className="ml-auto">{new Date(call.created_at).toLocaleString()}</span>
                  </div>
                  {call.transcript && (
                    <p className="mt-2 text-sm text-zinc-500 truncate">
                      {call.transcript}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
