'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Phone, Search, Filter, Download, Play, ChevronDown,
  Calendar, User, Clock, MessageSquare, Loader2
} from 'lucide-react'
import { api } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface Call {
  id: number
  caller_phone: string
  duration_seconds: number | null
  transcript: string | null
  sentiment: string | null
  outcome: string | null
  created_at: string
}

export default function CallsPage() {
  const { user, loading: authLoading } = useAuth();
  const [calls, setCalls] = useState<Call[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState('')
  const [expandedCall, setExpandedCall] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    const fetchCalls = async () => {
      if (!user) return;
      setLoading(true);
      try {
        const res = await api.calls.history(user.company_id, page, 20, { 
          phone: search, 
          sentiment: sentimentFilter 
        });
        setCalls(res.data.calls);
        setTotal(res.data.total);
      } catch (err) {
        console.error('Error fetching calls:', err);
      } finally {
        setLoading(false);
      }
    };
    
    // Add simple debounce for search
    const timer = setTimeout(() => fetchCalls(), 300);
    return () => clearTimeout(timer);
  }, [user, page, search, sentimentFilter]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground">Loading calls...</p>
      </div>
    )
  }

  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString()
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const sentimentColors: Record<string, string> = {
    POSITIVE: 'bg-green-500/20 text-green-500',
    NEUTRAL: 'bg-gray-500/20 text-gray-500',
    FRUSTRATED: 'bg-orange-500/20 text-orange-500',
    ANGRY: 'bg-red-500/20 text-red-500',
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border glass sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Phone className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground">VoiceCore</span>
            </Link>
            <div className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition">Dashboard</Link>
              <Link href="/agents" className="text-muted-foreground hover:text-foreground transition">Agents</Link>
              <Link href="/calls" className="text-primary font-medium">Calls</Link>
              <Link href="/analytics" className="text-muted-foreground hover:text-foreground transition">Analytics</Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Call History</h1>
            <p className="text-muted-foreground">View and manage all your calls</p>
          </div>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        <div className="card p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by phone number..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field w-full pr-10"
              />
            </div>
            <div className="flex gap-4">
              <select
                value={sentimentFilter}
                onChange={(e) => setSentimentFilter(e.target.value)}
                className="input-field"
              >
                <option value="">All Sentiments</option>
                <option value="POSITIVE">Positive</option>
                <option value="NEUTRAL">Neutral</option>
                <option value="FRUSTRATED">Frustrated</option>
                <option value="ANGRY">Angry</option>
              </select>
              <button className="btn-secondary flex items-center gap-2">
                <Filter className="w-4 h-4" />
                More Filters
              </button>
            </div>
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/50">
                <tr>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground">Date</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground">Phone</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground">Duration</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground">Sentiment</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground">Outcome</th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-muted-foreground"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {calls.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">
                      No calls found matching your criteria.
                    </td>
                  </tr>
                ) : calls.map((call) => (
                  <React.Fragment key={call.id}>
                    <tr className="hover:bg-secondary/30 transition">
                      <td className="px-6 py-4 text-foreground">{formatDate(call.created_at)}</td>
                      <td className="px-6 py-4 text-foreground font-mono">{call.caller_phone}</td>
                      <td className="px-6 py-4 text-foreground">{formatDuration(call.duration_seconds)}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs ${sentimentColors[call.sentiment || 'NEUTRAL']}`}>
                          {call.sentiment || 'NEUTRAL'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">{call.outcome || 'N/A'}</td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => setExpandedCall(expandedCall === call.id ? null : call.id)}
                          className="p-2 hover:bg-secondary rounded-lg transition"
                        >
                          <Play className="w-4 h-4 text-primary" />
                        </button>
                      </td>
                    </tr>
                    {expandedCall === call.id && (
                      <tr>
                        <td colSpan={6} className="px-6 py-4 bg-secondary/20">
                          <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">Transcript:</p>
                            <p className="text-foreground text-sm">{call.transcript || 'No transcript available'}</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-6 py-4 border-t border-border flex items-center justify-between">
            <p className="text-muted-foreground text-sm">Showing {calls.length} calls</p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary px-3 py-1 text-sm"
              >
                Previous
              </button>
              <span className="text-foreground">Page {page}</span>
              <button
                onClick={() => setPage(page + 1)}
                className="btn-secondary px-3 py-1 text-sm"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
