'use client';

import { useState } from 'react';
import { 
  Calculator, DollarSign, Phone, Users, TrendingUp,
  Building2, BarChart3, Clock, CheckCircle
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area
} from 'recharts';

const VERTICALS = [
  { id: 'general', name: 'General Business', avg_value: 1500, missed_rate: 30 },
  { id: 'dental', name: 'Dental', avg_value: 1500, missed_rate: 35 },
  { id: 'legal', name: 'Legal', avg_value: 5000, missed_rate: 42 },
  { id: 'realty', name: 'Realty', avg_value: 25000, missed_rate: 67 },
  { id: 'medical', name: 'Medical', avg_value: 3000, missed_rate: 38 },
  { id: 'auto', name: 'Auto Dealer', avg_value: 8000, missed_rate: 55 },
];

const PLANS = [
  { name: 'starter', price: 299, receptionist: 3000 },
  { name: 'business', price: 899, receptionist: 5000 },
  { name: 'enterprise', price: 2499, receptionist: 8000 },
];

export default function ROIPage() {
  const [vertical, setVertical] = useState('dental');
  const [monthlyCalls, setMonthlyCalls] = useState(500);
  const [receptionistSalary, setReceptionistSalary] = useState(3500);
  const [selectedPlan, setSelectedPlan] = useState('business');

  const currentVertical = VERTICALS.find(v => v.id === vertical) || VERTICALS[0];
  const currentPlan = PLANS.find(p => p.name === selectedPlan) || PLANS[1];

  const missedCalls = monthlyCalls * (currentVertical.missed_rate / 100);
  const callsAnswered = missedCalls * 0.95;
  const newCustomers = callsAnswered * 0.30;
  const revenueRecovered = newCustomers * currentVertical.avg_value;
  const salarySavings = receptionistSalary - currentPlan.price;
  const totalMonthlyBenefit = revenueRecovered + salarySavings;
  const annualBenefit = totalMonthlyBenefit * 12;
  const roi = ((annualBenefit - currentPlan.price * 12) / (currentPlan.price * 12)) * 100;

  const planComparisonData = PLANS.map(plan => ({
    name: plan.name.charAt(0).toUpperCase() + plan.name.slice(1),
    cost: plan.price,
    benefit: plan.name === 'starter' ? revenueRecovered + 2500 :
             plan.name === 'business' ? revenueRecovered + 4500 :
             revenueRecovered + 7000,
    roi: ((plan.name === 'starter' ? revenueRecovered + 2500 :
           plan.name === 'business' ? revenueRecovered + 4500 :
           revenueRecovered + 7000 - plan.price) / plan.price) * 100
  }));

  const yearlyTrend = Array.from({ length: 12 }, (_, i) => ({
    month: `M${i + 1}`,
    revenue: Math.floor(totalMonthlyBenefit * (1 + i * 0.02)),
    cost: currentPlan.price
  }));

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">ROI Calculator</h2>
        <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-lg">
          <TrendingUp className="w-5 h-5 text-green-500" />
          <span className="text-green-500 font-medium">{roi.toFixed(0)}% Annual ROI</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Configuration</h3>
            
            <div>
              <label className="block text-sm text-zinc-400 mb-2">Industry Vertical</label>
              <select
                value={vertical}
                onChange={(e) => setVertical(e.target.value)}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              >
                {VERTICALS.map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-zinc-400 mb-2">Monthly Calls Received</label>
              <input
                type="number"
                value={monthlyCalls}
                onChange={(e) => setMonthlyCalls(Number(e.target.value))}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-400 mb-2">Current Receptionist Salary</label>
              <input
                type="number"
                value={receptionistSalary}
                onChange={(e) => setReceptionistSalary(Number(e.target.value))}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-400 mb-2">Plan</label>
              <select
                value={selectedPlan}
                onChange={(e) => setSelectedPlan(e.target.value)}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2 text-white"
              >
                {PLANS.map(p => (
                  <option key={p.name} value={p.name}>
                    {p.name.charAt(0).toUpperCase() + p.name.slice(1)} - {formatCurrency(p.price)}/mo
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Key Metrics</h3>
            
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Missed Calls</span>
              <span className="text-white font-medium">{missedCalls.toFixed(0)} ({currentVertical.missed_rate}%)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Calls Answered by AI</span>
              <span className="text-green-500 font-medium">{callsAnswered.toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">New Customers</span>
              <span className="text-white font-medium">{newCustomers.toFixed(1)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400">Avg Customer Value</span>
              <span className="text-white font-medium">{formatCurrency(currentVertical.avg_value)}</span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-2 text-zinc-400 mb-2">
                <DollarSign className="w-4 h-4" />
                Monthly Benefit
              </div>
              <p className="text-2xl font-bold text-white">{formatCurrency(totalMonthlyBenefit)}</p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-2 text-zinc-400 mb-2">
                <TrendingUp className="w-4 h-4" />
                Annual Benefit
              </div>
              <p className="text-2xl font-bold text-green-500">{formatCurrency(annualBenefit)}</p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-2 text-zinc-400 mb-2">
                <Clock className="w-4 h-4" />
                Payback Period
              </div>
              <p className="text-2xl font-bold text-white">{(currentPlan.price / totalMonthlyBenefit * 30).toFixed(0)} days</p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-2 text-zinc-400 mb-2">
                <BarChart3 className="w-4 h-4" />
                3-Year ROI
              </div>
              <p className="text-2xl font-bold text-amber-500">{((annualBenefit * 3 - currentPlan.price * 36) / (currentPlan.price * 36) * 100).toFixed(0)}%</p>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Yearly Projection</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={yearlyTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                <XAxis dataKey="month" stroke="#71717a" fontSize={12} />
                <YAxis stroke="#71717a" fontSize={12} tickFormatter={(v) => `$${v/1000}k`} />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Area type="monotone" dataKey="revenue" stroke="#22c55e" fill="#22c55e" fillOpacity={0.2} />
                <Area type="monotone" dataKey="cost" stroke="#ef4444" fill="#ef4444" fillOpacity={0.1} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Plan Comparison</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={planComparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                <XAxis dataKey="name" stroke="#71717a" fontSize={12} />
                <YAxis stroke="#71717a" fontSize={12} tickFormatter={(v) => `${v}%`} />
                <Tooltip formatter={(value: number) => `${value.toFixed(0)}%`} />
                <Bar dataKey="roi" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
              <div>
                <h4 className="text-lg font-semibold text-white">Bottom Line</h4>
                <p className="text-zinc-300 mt-2">
                  With <strong className="text-white">{currentVertical.name}</strong> receiving{' '}
                  <strong className="text-white">{monthlyCalls} calls/month</strong>, VoiceCore can recover{' '}
                  <strong className="text-green-500">{formatCurrency(revenueRecovered)}</strong> in lost revenue
                  plus save <strong className="text-green-500">{formatCurrency(salarySavings)}</strong> on
                  receptionist costs, for a total monthly benefit of{' '}
                  <strong className="text-green-500">{formatCurrency(totalMonthlyBenefit)}</strong>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
