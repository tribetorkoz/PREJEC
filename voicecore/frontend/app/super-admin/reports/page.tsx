'use client';

import { useState } from 'react';
import { 
  FileText, Download, Calendar, TrendingUp, 
  Users, Phone, DollarSign, Filter, BarChart3
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area
} from 'recharts';

const REPORTS = [
  {
    id: '1',
    name: 'Monthly Revenue Report',
    description: 'Complete breakdown of MRR, ARR, and plan distribution',
    type: 'financial',
    frequency: 'monthly',
    last_generated: '2024-03-01T00:00:00Z',
    size: '2.4 MB'
  },
  {
    id: '2',
    name: 'Call Analytics Summary',
    description: 'Total calls, duration, sentiment analysis, and outcomes',
    type: 'analytics',
    frequency: 'daily',
    last_generated: '2024-03-15T00:00:00Z',
    size: '1.8 MB'
  },
  {
    id: '3',
    name: 'Customer Churn Report',
    description: 'Churned companies, reasons, and retention metrics',
    type: 'retention',
    frequency: 'monthly',
    last_generated: '2024-03-01T00:00:00Z',
    size: '0.8 MB'
  },
  {
    id: '4',
    name: 'Agent Performance',
    description: 'Agent-level metrics including resolution rates and call handling',
    type: 'performance',
    frequency: 'weekly',
    last_generated: '2024-03-10T00:00:00Z',
    size: '3.2 MB'
  },
  {
    id: '5',
    name: 'Provider Usage Report',
    description: 'API usage and costs for STT, LLM, and TTS providers',
    type: 'operations',
    frequency: 'weekly',
    last_generated: '2024-03-10T00:00:00Z',
    size: '1.1 MB'
  },
  {
    id: '6',
    name: 'HIPAA Compliance Audit',
    description: 'PHI access logs, BAA status, and compliance metrics',
    type: 'compliance',
    frequency: 'monthly',
    last_generated: '2024-03-01T00:00:00Z',
    size: '0.5 MB'
  },
];

const MONTHLY_DATA = [
  { month: 'Jan', revenue: 42000, calls: 8500, clients: 85 },
  { month: 'Feb', revenue: 48000, calls: 10200, clients: 98 },
  { month: 'Mar', revenue: 55000, calls: 12500, clients: 115 },
  { month: 'Apr', revenue: 62000, calls: 14800, clients: 132 },
  { month: 'May', revenue: 71000, calls: 17200, clients: 155 },
  { month: 'Jun', revenue: 82000, calls: 19500, clients: 178 },
  { month: 'Jul', revenue: 95000, calls: 22100, clients: 205 },
  { month: 'Aug', revenue: 108000, calls: 24800, clients: 232 },
  { month: 'Sep', revenue: 122000, calls: 27500, clients: 258 },
  { month: 'Oct', revenue: 138000, calls: 30200, clients: 285 },
  { month: 'Nov', revenue: 155000, calls: 32800, clients: 312 },
  { month: 'Dec', revenue: 172000, calls: 35500, clients: 338 },
];

export default function ReportsPage() {
  const [reportType, setReportType] = useState<string>('all');
  const [dateRange, setDateRange] = useState('30d');

  const filteredReports = reportType === 'all' 
    ? REPORTS 
    : REPORTS.filter(r => r.type === reportType);

  const formatDate = (date: string) => new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'financial': return <DollarSign className="w-4 h-4" />;
      case 'analytics': return <BarChart3 className="w-4 h-4" />;
      case 'retention': return <Users className="w-4 h-4" />;
      case 'performance': return <TrendingUp className="w-4 h-4" />;
      case 'compliance': return <FileText className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'financial': return 'bg-green-500/10 text-green-500';
      case 'analytics': return 'bg-blue-500/10 text-blue-500';
      case 'retention': return 'bg-purple-500/10 text-purple-500';
      case 'performance': return 'bg-amber-500/10 text-amber-500';
      case 'compliance': return 'bg-red-500/10 text-red-500';
      default: return 'bg-zinc-800 text-zinc-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Reports & Analytics</h2>
          <p className="text-zinc-400 mt-1">Generate and download business reports</p>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-white"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="12m">Last 12 months</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-zinc-950 font-medium rounded-lg hover:bg-amber-600">
            <Download className="w-4 h-4" />
            Export All
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Growth Overview</h3>
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setReportType('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  reportType === 'all' ? 'bg-amber-500 text-zinc-950' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setReportType('financial')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  reportType === 'financial' ? 'bg-green-500 text-white' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                Financial
              </button>
              <button
                onClick={() => setReportType('analytics')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  reportType === 'analytics' ? 'bg-blue-500 text-white' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                Analytics
              </button>
              <button
                onClick={() => setReportType('compliance')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  reportType === 'compliance' ? 'bg-red-500 text-white' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                Compliance
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={MONTHLY_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                <XAxis dataKey="month" stroke="#71717a" fontSize={12} />
                <YAxis stroke="#71717a" fontSize={12} tickFormatter={(v) => `$${v/1000}k`} />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Area type="monotone" dataKey="revenue" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Available Reports</h3>
            <div className="space-y-3">
              {filteredReports.map((report) => (
                <div key={report.id} className="bg-zinc-800 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getTypeColor(report.type)}`}>
                      {getTypeIcon(report.type)}
                    </div>
                    <div>
                      <p className="text-white font-medium">{report.name}</p>
                      <p className="text-zinc-500 text-sm">{report.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-zinc-400 text-sm">Last generated</p>
                      <p className="text-white text-sm">{formatDate(report.last_generated)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-zinc-400 text-sm">Size</p>
                      <p className="text-white text-sm">{report.size}</p>
                    </div>
                    <button className="px-4 py-2 bg-zinc-700 text-white text-sm rounded-lg hover:bg-zinc-600 flex items-center gap-2">
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-zinc-400">Total Reports</span>
                <span className="text-white font-medium">{REPORTS.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400">Auto-generated</span>
                <span className="text-green-500 font-medium">{REPORTS.filter(r => r.frequency !== 'manual').length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400">Total Size</span>
                <span className="text-white font-medium">9.8 MB</span>
              </div>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Monthly Breakdown</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={MONTHLY_DATA.slice(-6)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                <XAxis dataKey="month" stroke="#71717a" fontSize={12} />
                <YAxis stroke="#71717a" fontSize={12} />
                <Tooltip />
                <Bar dataKey="clients" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Schedule Report</h3>
            <div className="space-y-3">
              <button className="w-full px-4 py-3 bg-zinc-800 text-white text-sm rounded-lg hover:bg-zinc-700 text-left flex items-center gap-3">
                <Calendar className="w-4 h-4 text-zinc-400" />
                Daily Summary (8:00 AM)
              </button>
              <button className="w-full px-4 py-3 bg-zinc-800 text-white text-sm rounded-lg hover:bg-zinc-700 text-left flex items-center gap-3">
                <Calendar className="w-4 h-4 text-zinc-400" />
                Weekly Report (Monday 9:00 AM)
              </button>
              <button className="w-full px-4 py-3 bg-zinc-800 text-white text-sm rounded-lg hover:bg-zinc-700 text-left flex items-center gap-3">
                <Calendar className="w-4 h-4 text-zinc-400" />
                Monthly Report (1st of month)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
