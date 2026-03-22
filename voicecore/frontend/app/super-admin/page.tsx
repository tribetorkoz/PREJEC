'use client';

import { useEffect, useState } from 'react';
import { adminDashboard } from '@/lib/admin-api';
import { 
  DollarSign, Users, Phone, AlertTriangle, TrendingUp, 
  TrendingDown, Activity, BarChart3
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, AreaChart, Area
} from 'recharts';

interface DashboardData {
  kpis: {
    mrr: number;
    arr: number;
    total_clients: number;
    active_clients: number;
    calls_today: number;
    calls_this_month: number;
    failed_calls: number;
    failed_calls_rate: number;
    sentiment_breakdown: Record<string, number>;
    plans_breakdown: Record<string, number>;
  };
  charts: {
    revenue_growth: { month: string; clients: number }[];
    clients_per_month: { month: string; clients: number }[];
    calls_volume: { date: string; calls: number }[];
  };
}

export default function AdminDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const result = await adminDashboard.getData();
      setData(result);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  const kpis = data?.kpis || {
    mrr: 0,
    arr: 0,
    total_clients: 0,
    active_clients: 0,
    calls_today: 0,
    calls_this_month: 0,
    failed_calls: 0,
    failed_calls_rate: 0
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">MRR</p>
              <p className="text-2xl font-bold text-white mt-1">{formatCurrency(kpis.mrr)}</p>
            </div>
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-500" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm text-green-500">
            <TrendingUp className="w-4 h-4" />
            <span>Monthly Recurring</span>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Total Clients</p>
              <p className="text-2xl font-bold text-white mt-1">{kpis.total_clients}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-500" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm text-zinc-400">
            <span>{kpis.active_clients} active</span>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Calls Today</p>
              <p className="text-2xl font-bold text-white mt-1">{kpis.calls_today}</p>
            </div>
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <Phone className="w-6 h-6 text-purple-500" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm text-zinc-400">
            <span>{kpis.calls_this_month} this month</span>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Failed Calls</p>
              <p className="text-2xl font-bold text-white mt-1">{kpis.failed_calls}</p>
            </div>
            <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm text-zinc-400">
            <span>{kpis.failed_calls_rate}% rate</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Revenue Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data?.charts.revenue_growth || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
              <XAxis dataKey="month" stroke="#71717a" fontSize={12} />
              <YAxis stroke="#71717a" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="clients" stroke="#f59e0b" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Clients per Month</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data?.charts.clients_per_month || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
              <XAxis dataKey="month" stroke="#71717a" fontSize={12} />
              <YAxis stroke="#71717a" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="clients" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Calls Volume (Last 30 Days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data?.charts.calls_volume || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis dataKey="date" stroke="#71717a" fontSize={12} />
            <YAxis stroke="#71717a" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46' }}
              labelStyle={{ color: '#fff' }}
            />
            <Area type="monotone" dataKey="calls" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
