'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Phone, Search, Filter, Download, Play, Calendar } from 'lucide-react';

interface Call {
  id: number;
  caller_phone: string;
  duration_seconds: number;
  sentiment: string;
  outcome: string;
  transcript: string;
  created_at: string;
}

export default function CallsPage() {
  const [calls, setCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadCalls();
  }, [page]);

  const loadCalls = async () => {
    try {
      const data = await api.calls.list({ page, limit: 20 });
      setCalls(data.calls || []);
      setTotalPages(data.pages || 1);
    } catch (error) {
      console.error('Failed to load calls:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'POSITIVE': return 'text-green-500 bg-green-500/10';
      case 'NEUTRAL': return 'text-yellow-500 bg-yellow-500/10';
      case 'ANGRY': return 'text-red-500 bg-red-500/10';
      default: return 'text-zinc-400 bg-zinc-800';
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredCalls = calls.filter(c => 
    c.caller_phone.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Call History</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by phone number..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
          <Filter className="w-4 h-4" />
          Filter
        </button>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Date</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Caller</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Duration</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Sentiment</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Outcome</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-zinc-500">Loading...</td>
              </tr>
            ) : filteredCalls.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-zinc-500">No calls found</td>
              </tr>
            ) : (
              filteredCalls.map((call) => (
                <tr key={call.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                  <td className="p-4 text-zinc-400">
                    {call.created_at ? new Date(call.created_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="p-4 text-white font-mono">{call.caller_phone}</td>
                  <td className="p-4 text-zinc-300">
                    {call.duration_seconds ? formatDuration(call.duration_seconds) : '-'}
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded ${getSentimentColor(call.sentiment || '')}`}>
                      {call.sentiment || 'N/A'}
                    </span>
                  </td>
                  <td className="p-4 text-zinc-400">{call.outcome || '-'}</td>
                  <td className="p-4">
                    <button className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded">
                      <Play className="w-4 h-4" />
                    </button>
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
