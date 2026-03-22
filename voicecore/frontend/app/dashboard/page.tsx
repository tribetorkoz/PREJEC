'use client'

import { useEffect, useState, Suspense } from 'react'
import Link from 'next/link'
import { 
  Phone, PhoneCall, Clock, TrendingUp, Users, 
  Play, ChevronRight, Activity, AlertCircle,
  BarChart3, MessageSquare, Settings
} from 'lucide-react'
import { callsApi, analyticsApi } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface Stats {
  total_calls: number
  total_duration_seconds: number
  avg_duration_seconds: number
}

interface CallAnalytics {
  total_calls: number
  total_duration: number
  avg_duration: number
  calls_today: number
  calls_this_week: number
  calls_this_month: number
  sentiment_breakdown: Record<string, number>
  outcome_breakdown: Record<string, number>
}

interface RecentCall {
  id: number
  caller_phone: string
  duration_seconds: number | null
  sentiment: string | null
  outcome: string | null
  created_at: string
}

function StatsCard({ title, value, icon: Icon, trend }: { title: string, value: string | number, icon: React.ElementType, trend?: string }) {
  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-muted-foreground text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-foreground">{value}</p>
          {trend && (
            <p className="text-green-500 text-sm mt-1 flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              {trend}
            </p>
          )}
        </div>
        <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-primary" />
        </div>
      </div>
    </div>
  )
}

function SentimentChart({ data }: { data: Record<string, number> }) {
  const colors: Record<string, string> = {
    POSITIVE: 'bg-green-500',
    NEUTRAL: 'bg-gray-500',
    FRUSTRATED: 'bg-orange-500',
    ANGRY: 'bg-red-500',
  }
  
  const total = Object.values(data).reduce((a, b) => a + b, 0)
  
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">Sentiment Analysis</h3>
      <div className="space-y-3">
        {Object.entries(data).map(([sentiment, count]) => (
          <div key={sentiment} className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${colors[sentiment] || 'bg-gray-500'}`} />
            <span className="text-muted-foreground flex-1">{sentiment}</span>
            <span className="text-foreground font-medium">
              {total > 0 ? Math.round((count / total) * 100) : 0}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function RecentCalls({ calls }: { calls: RecentCall[] }) {
  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }
  
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }
  
  const sentimentColors: Record<string, string> = {
    POSITIVE: 'text-green-500',
    NEUTRAL: 'text-gray-500',
    FRUSTRATED: 'text-orange-500',
    ANGRY: 'text-red-500',
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Recent Calls</h3>
        <Link href="/calls" className="text-primary text-sm hover:underline flex items-center gap-1">
          View all <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
      <div className="space-y-3">
        {calls.slice(0, 5).map((call) => (
          <div key={call.id} className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                <Phone className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-foreground font-medium">{call.caller_phone}</p>
                <p className="text-muted-foreground text-sm">{formatTime(call.created_at)}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className={`text-sm ${sentimentColors[call.sentiment || 'NEUTRAL']}`}>
                {call.sentiment || 'NEUTRAL'}
              </span>
              <span className="text-muted-foreground text-sm">{formatDuration(call.duration_seconds)}</span>
              {call.duration_seconds && (
                <button className="p-2 hover:bg-primary/10 rounded-lg transition">
                  <Play className="w-4 h-4 text-primary" />
                </button>
              )}
            </div>
          </div>
        ))}
        {calls.length === 0 && (
          <p className="text-muted-foreground text-center py-8">No recent calls</p>
        )}
      </div>
    </div>
  )
}

function AgentStatus({ isOnline, onToggle }: { isOnline: boolean, onToggle: () => void }) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Agent Status</h3>
        <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-foreground font-medium">Voice Agent</p>
          <p className="text-muted-foreground text-sm">
            {isOnline ? 'Online & answering calls' : 'Offline'}
          </p>
        </div>
        <button
          onClick={onToggle}
          className={`relative w-16 h-8 rounded-full transition-colors ${
            isOnline ? 'bg-green-500' : 'bg-gray-600'
          }`}
        >
          <div className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
            isOnline ? 'translate-x-9' : 'translate-x-1'
          }`} />
        </button>
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card p-6">
            <div className="h-4 bg-secondary rounded w-1/2 mb-4 animate-pulse" />
            <div className="h-8 bg-secondary rounded w-3/4 animate-pulse" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth()
  const [stats, setStats] = useState<Stats | null>(null)
  const [analytics, setAnalytics] = useState<CallAnalytics | null>(null)
  const [recentCalls, setRecentCalls] = useState<RecentCall[]>([])
  const [isAgentOnline, setIsAgentOnline] = useState(true)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      if (!user) return;
      try {
        const [analyticsRes, callsRes] = await Promise.all([
          analyticsApi.getSummary(user.company_id),
          callsApi.list(user.company_id, 10)
        ])
        setAnalytics(analyticsRes.data)
        setRecentCalls(callsRes.data)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [user])

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  const formatDuration = (seconds: number) => {
    if (!seconds) return '0m 0s'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
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
              <Link href="/dashboard" className="text-primary font-medium">Dashboard</Link>
              <Link href="/agents" className="text-muted-foreground hover:text-foreground transition">Agents</Link>
              <Link href="/calls" className="text-muted-foreground hover:text-foreground transition">Calls</Link>
              <Link href="/analytics" className="text-muted-foreground hover:text-foreground transition">Analytics</Link>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-foreground mr-2">{user?.email}</span>
              <button className="p-2 hover:bg-secondary rounded-lg transition">
                <Activity className="w-5 h-5 text-muted-foreground" />
              </button>
              <button className="p-2 hover:bg-secondary rounded-lg transition">
                <Settings className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your call overview.</p>
          </div>
          <Link href="/agents" className="btn-primary">
            <PhoneCall className="w-4 h-4 mr-2" />
            Test Call
          </Link>
        </div>

        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid md:grid-cols-4 gap-6">
              <StatsCard 
                title="Calls Today" 
                value={analytics?.calls_today || 0} 
                icon={PhoneCall}
                trend="+12%"
              />
              <StatsCard 
                title="Calls This Week" 
                value={analytics?.calls_this_week || 0} 
                icon={Phone}
                trend="+8%"
              />
              <StatsCard 
                title="Avg Duration" 
                value={formatDuration(analytics?.avg_duration || 0)} 
                icon={Clock}
              />
              <StatsCard 
                title="Missed Calls" 
                value={0} 
                icon={AlertCircle}
                trend="0%"
              />
            </div>

            {/* Charts Row */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <RecentCalls calls={recentCalls} />
              </div>
              <div className="space-y-6">
                <AgentStatus 
                  isOnline={isAgentOnline} 
                  onToggle={() => setIsAgentOnline(!isAgentOnline)} 
                />
                <SentimentChart data={analytics?.sentiment_breakdown || {}} />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
              <div className="flex flex-wrap gap-4">
                <Link href="/agents" className="btn-primary">
                  <Settings className="w-4 h-4 mr-2" />
                  Configure Agent
                </Link>
                <Link href="/calls" className="btn-secondary">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  View All Calls
                </Link>
                <Link href="/analytics" className="btn-secondary">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Analytics Report
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
