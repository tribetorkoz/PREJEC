'use client';

import { useEffect, useState } from 'react';
import { adminCalls, Call } from '@/lib/admin-api';
import { Search, Phone, PhoneOff, Clock, Filter, Download } from 'lucide-react';

export default function CallsPage() {
  const [calls, setCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'live' | 'history'>('live');
  const [search, setSearch] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadCalls();
  }, [tab, sentiment, page]);

  useEffect(() => {
    if (tab === 'live') {
      const interval = setInterval(loadCalls, 5000);
      return () => clearInterval(interval);
    }
  }, [tab]);

  const loadCalls = async () => {
    try {
      if (tab === 'live') {
        const result = await adminCalls.getLive();
        setCalls(result.calls);
      } else {
        const result = await adminCalls.getHistory({
          sentiment: sentiment || undefined,
          page,
        });
        setCalls(result.calls);
      }
    } catch (error) {
      console.error('Failed to load calls:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (s: string) => {
    switch (s) {
      case 'POSITIVE': return 'bg-green-500/10 text-green-500';
      case 'NEUTRAL': return 'bg-yellow-500/10 text-yellow-500';
      case 'ANGRY': return 'bg-red-500/10 text-red-500';
      case 'FRUSTRATED': return 'bg-orange-500/10 text-orange-500';
      default: return 'bg-zinc-800 text-zinc-400';
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredCalls = calls.filter(c => 
    c.caller_phone.includes(search) || 
    c.company_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Call Monitor</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700">
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setTab('live')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            tab === 'live' ? 'bg-amber-500 text-zinc-950' : 'bg-zinc-800 text-zinc-400 hover:text-white'
          }`}
        >
          <Phone className="w-4 h-4 inline-block mr-2" />
          Live Calls
        </button>
        <button
          onClick={() => setTab('history')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            tab === 'history' ? 'bg-amber-500 text-zinc-950' : 'bg-zinc-800 text-zinc-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4 inline-block mr-2" />
          Call History
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search calls..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        {tab === 'history' && (
          <select
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <option value="">All Sentiments</option>
            <option value="POSITIVE">Positive</option>
            <option value="NEUTRAL">Neutral</option>
            <option value="FRUSTRATED">Frustrated</option>
            <option value="ANGRY">Angry</option>
          </select>
        )}
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left p-4 text-zinc-400 font-medium">Company</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Caller</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Duration</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Sentiment</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Outcome</th>
              <th className="text-left p-4 text-zinc-400 font-medium">Time</th>
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
                  <td className="p-4 text-white font-medium">{call.company_name}</td>
                  <td className="p-4 text-zinc-300">{call.caller_phone}</td>
                  <td className="p-4 text-zinc-300">
                    {call.duration_seconds ? formatDuration(call.duration_seconds) : '-'}
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded ${getSentimentColor(call.sentiment || '')}`}>
                      {call.sentiment || 'N/A'}
                    </span>
                  </td>
                  <td className="p-4 text-zinc-400">{call.outcome || '-'}</td>
                  <td className="p-4 text-zinc-400 text-sm">
                    {call.created_at ? new Date(call.created_at).toLocaleString() : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {tab === 'history' && (
        <div className="flex items-center justify-between">
          <p className="text-zinc-400">Page {page}</p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-zinc-800 text-white rounded-lg disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={calls.length === 0}
              className="px-4 py-2 bg-zinc-800 text-white rounded-lg disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
