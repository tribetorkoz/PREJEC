'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Phone, BarChart3, TrendingUp, Clock, MessageSquare,
  PieChart, Calendar, Loader2
} from 'lucide-react'
import { api } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { 
  LineChart, Line, BarChart, Bar, PieChart as RechartsPie, 
  Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts'

const callsByDay = [
  { date: 'Jan 1', calls: 45 },
  { date: 'Jan 2', calls: 52 },
  { date: 'Jan 3', calls: 38 },
  { date: 'Jan 4', calls: 65 },
  { date: 'Jan 5', calls: 48 },
  { date: 'Jan 6', calls: 42 },
  { date: 'Jan 7', calls: 55 },
]

const peakHours = [
  { hour: '9 AM', calls: 12 },
  { hour: '10 AM', calls: 25 },
  { hour: '11 AM', calls: 35 },
  { hour: '12 PM', calls: 20 },
  { hour: '1 PM', calls: 15 },
  { hour: '2 PM', calls: 30 },
  { hour: '3 PM', calls: 45 },
  { hour: '4 PM', calls: 38 },
  { hour: '5 PM', calls: 22 },
]

const outcomes = [
  { name: 'Completed', value: 65, color: '#22c55e' },
  { name: 'Voicemail', value: 15, color: '#f59e0b' },
  { name: 'Missed', value: 10, color: '#ef4444' },
  { name: 'Transferred', value: 10, color: '#3b82f6' },
]

const topQuestions = [
  { question: 'What are your hours?', count: 145 },
  { question: 'Book appointment', count: 132 },
  { question: 'Pricing information', count: 98 },
  { question: 'Location details', count: 87 },
  { question: 'Cancel appointment', count: 65 },
]

const sentimentTrend = [
  { week: 'W1', positive: 60, neutral: 30, negative: 10 },
  { week: 'W2', positive: 65, neutral: 25, negative: 10 },
  { week: 'W3', positive: 70, neutral: 22, negative: 8 },
  { week: 'W4', positive: 75, neutral: 18, negative: 7 },
]

export default function AnalyticsPage() {
  const { user, loading: authLoading } = useAuth();
  const [timeRange, setTimeRange] = useState('30d')
  const [loading, setLoading] = useState(false)

  // Wait for authentication before rendering data
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground">Loading your analytics...</p>
      </div>
    )
  }

  if (!user) {
    return null; // Will be redirected by AuthContext
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
              <Link href="/calls" className="text-muted-foreground hover:text-foreground transition">Calls</Link>
              <Link href="/analytics" className="text-primary font-medium">Analytics</Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
            <p className="text-muted-foreground">Track your call performance and insights</p>
          </div>
          <div className="flex items-center gap-2">
            {['7d', '30d', '90d'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  timeRange === range 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-secondary text-muted-foreground hover:text-foreground'
                }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-2">
              <Phone className="w-5 h-5 text-primary" />
              <span className="text-green-500 text-sm flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> +12%
              </span>
            </div>
            <p className="text-3xl font-bold text-foreground">1,247</p>
            <p className="text-muted-foreground text-sm">Total Calls</p>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-5 h-5 text-primary" />
              <span className="text-green-500 text-sm flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> +8%
              </span>
            </div>
            <p className="text-3xl font-bold text-foreground">4:32</p>
            <p className="text-muted-foreground text-sm">Avg Duration</p>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between mb-2">
              <MessageSquare className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold text-foreground">75%</p>
            <p className="text-muted-foreground text-sm">Positive Sentiment</p>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between mb-2">
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold text-foreground">0%</p>
            <p className="text-muted-foreground text-sm">Missed Calls</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Calls Per Day
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={callsByDay}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: '#f9fafb' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="calls" 
                  stroke="#f59e0b" 
                  strokeWidth={3}
                  dot={{ fill: '#f59e0b' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              Peak Hours
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={peakHours}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="hour" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: '#f9fafb' }}
                />
                <Bar dataKey="calls" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-primary" />
              Call Outcomes
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <RechartsPie>
                <Pie
                  data={outcomes}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {outcomes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
              </RechartsPie>
            </ResponsiveContainer>
          </div>

          <div className="card p-6 lg:col-span-2">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-primary" />
              Sentiment Trend
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sentimentTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="week" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Legend />
                <Bar dataKey="positive" stackId="a" fill="#22c55e" />
                <Bar dataKey="neutral" stackId="a" fill="#9ca3af" />
                <Bar dataKey="negative" stackId="a" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            Top Questions Asked by Customers
          </h3>
          <div className="space-y-3">
            {topQuestions.map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                <span className="text-foreground">{item.question}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full" 
                      style={{ width: `${(item.count / 150) * 100}%` }}
                    />
                  </div>
                  <span className="text-muted-foreground text-sm w-12 text-right">{item.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
