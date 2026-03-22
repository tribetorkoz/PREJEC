'use client';

import { useEffect, useState } from 'react';
import { 
  Activity, Server, Database, Zap, Globe, 
  TrendingUp, TrendingDown, CheckCircle, XCircle,
  RefreshCw, AlertTriangle
} from 'lucide-react';

export default function PlatformPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const [metricsRes, healthRes] = await Promise.all([
        fetch('/api/admin/platform/metrics', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/admin/platform/health', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      const metricsData = await metricsRes.json();
      const healthData = await healthRes.json();
      setMetrics(metricsData);
      setHealth(healthData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Platform Overview</h2>
        <button 
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 rounded-lg hover:bg-amber-600"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Health Status */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-6 h-6 text-amber-500" />
          <h3 className="text-lg font-semibold text-white">System Health</h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            health?.overall === 'healthy' 
              ? 'bg-green-500/10 text-green-500' 
              : 'bg-red-500/10 text-red-500'
          }`}>
            {health?.overall === 'healthy' ? 'Healthy' : 'Issues Detected'}
          </span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {health?.services && Object.entries(health.services).map(([key, value]: [string, any]) => (
            <div key={key} className="bg-zinc-800 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-zinc-400 capitalize">{key.replace('_', ' ')}</span>
                {value.status === 'healthy' ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500" />
                )}
              </div>
              {value.latency_ms && (
                <p className="text-lg font-semibold text-white">{value.latency_ms}ms</p>
              )}
              {value.connections && (
                <p className="text-lg font-semibold text-white">{value.connections}</p>
              )}
              {value.active_calls !== undefined && (
                <p className="text-lg font-semibold text-white">{value.active_calls}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Growth Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <TrendingUp className="w-4 h-4" />
            MRR
          </div>
          <p className="text-3xl font-bold text-white">${metrics?.growth?.mrr?.toLocaleString()}</p>
          <p className="text-sm text-green-500 mt-1">
            +{metrics?.growth?.mrr_growth_percent}% this month
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <TrendingUp className="w-4 h-4" />
            ARR
          </div>
          <p className="text-3xl font-bold text-white">${metrics?.growth?.arr?.toLocaleString()}</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <Server className="w-4 h-4" />
            Total Companies
          </div>
          <p className="text-3xl font-bold text-white">{metrics?.scale?.total_companies}</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <Activity className="w-4 h-4" />
            Uptime
          </div>
          <p className="text-3xl font-bold text-white">{metrics?.product?.uptime_percent}%</p>
        </div>
      </div>

      {/* Retention & Unit Economics */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Retention Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Churn Rate</span>
              <span className="text-white font-medium">{metrics?.retention?.churn_rate}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Net Revenue Retention</span>
              <span className="text-white font-medium">{metrics?.retention?.net_revenue_retention}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Avg. Company Lifetime</span>
              <span className="text-white font-medium">{metrics?.retention?.avg_company_lifetime_months} months</span>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Unit Economics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">ARPU</span>
              <span className="text-white font-medium">${metrics?.unit_economics?.arpu}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">CAC</span>
              <span className="text-white font-medium">${metrics?.unit_economics?.cac}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">LTV</span>
              <span className="text-white font-medium">${metrics?.unit_economics?.ltv}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">LTV:CAC Ratio</span>
              <span className="text-green-500 font-medium">{metrics?.unit_economics?.ltv_cac_ratio}x</span>
            </div>
          </div>
        </div>
      </div>

      {/* Product Metrics */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Product Performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{metrics?.product?.total_calls_handled?.toLocaleString()}</p>
            <p className="text-zinc-400 text-sm">Total Calls</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{metrics?.product?.calls_this_month?.toLocaleString()}</p>
            <p className="text-zinc-400 text-sm">Calls This Month</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{metrics?.product?.avg_resolution_rate}%</p>
            <p className="text-zinc-400 text-sm">Resolution Rate</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{metrics?.product?.avg_latency_ms}ms</p>
            <p className="text-zinc-400 text-sm">Avg Latency</p>
          </div>
        </div>
      </div>
    </div>
  );
}
