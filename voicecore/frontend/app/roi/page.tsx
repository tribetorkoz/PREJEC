'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Phone, ArrowRight, TrendingUp, DollarSign, Calendar, Users } from 'lucide-react';

type Tab = 'basic' | 'industry' | 'detailed';

export default function ROIPage() {
  const [activeTab, setActiveTab] = useState<Tab>('basic');
  const [monthlyCalls, setMonthlyCalls] = useState(500);
  const [avgCallValue, setAvgCallValue] = useState(200);
  const [missRate, setMissRate] = useState(35);

  const lostRevenue = monthlyCalls * (missRate / 100) * avgCallValue;

  let recommendedPlan = 'starter';
  let planCost = 99;
  if (monthlyCalls <= 50) {
    recommendedPlan = 'free';
    planCost = 0;
  } else if (monthlyCalls <= 500) {
    recommendedPlan = 'starter';
    planCost = 99;
  } else if (monthlyCalls <= 2000) {
    recommendedPlan = 'business';
    planCost = 399;
  } else {
    recommendedPlan = 'enterprise';
    planCost = 0;
  }

  const monthlySavings = lostRevenue - planCost;
  const yearlySavings = monthlySavings * 12;
  const paybackDays = lostRevenue > 0 && planCost > 0 ? (planCost / lostRevenue) * 30 : 0;

  const industries = [
    { id: 'dental', name: 'Dental', icon: '🦷' },
    { id: 'legal', name: 'Legal', icon: '⚖️' },
    { id: 'realty', name: 'Real Estate', icon: '🏠' },
  ];

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
                <Phone className="w-6 h-6 text-zinc-950" />
              </div>
              <span className="text-xl font-bold text-white">VoiceCore</span>
            </Link>
            <Link
              href="/signup"
              className="bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold px-4 py-2 rounded-lg transition"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">
              ROI Calculator
            </h1>
            <p className="text-xl text-zinc-400">
              Calculate how much money you could save with VoiceCore
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-8">
            {[
              { id: 'basic' as Tab, label: 'Basic Calculator' },
              { id: 'industry' as Tab, label: 'Industry Calculator' },
              { id: 'detailed' as Tab, label: 'Detailed Breakdown' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  activeTab === tab.id
                    ? 'bg-amber-500 text-zinc-950'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Calculator */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Inputs */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-white mb-6">Your Business</h2>

              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-zinc-300">Monthly calls received</label>
                    <span className="text-amber-500 font-bold">{monthlyCalls}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="5000"
                    step="50"
                    value={monthlyCalls}
                    onChange={(e) => setMonthlyCalls(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                  />
                  <div className="flex justify-between text-xs text-zinc-500 mt-1">
                    <span>0</span>
                    <span>5,000+</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-zinc-300">Average call value ($)</label>
                    <span className="text-amber-500 font-bold">${avgCallValue}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1000"
                    step="10"
                    value={avgCallValue}
                    onChange={(e) => setAvgCallValue(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                  />
                  <div className="flex justify-between text-xs text-zinc-500 mt-1">
                    <span>$0</span>
                    <span>$1,000+</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-zinc-300">Current miss rate (%)</label>
                    <span className="text-amber-500 font-bold">{missRate}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={missRate}
                    onChange={(e) => setMissRate(Number(e.target.value))}
                    className="w-full h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                  />
                  <div className="flex justify-between text-xs text-zinc-500 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <h2 className="text-xl font-semibold text-white mb-6">Your Potential ROI</h2>

              <div className="space-y-6">
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                  <div className="text-red-400 text-sm mb-1">Currently losing</div>
                  <div className="text-3xl font-bold text-red-500">
                    ${lostRevenue.toLocaleString()}
                    <span className="text-lg font-normal text-red-400">/month</span>
                  </div>
                </div>

                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
                  <div className="text-amber-500 text-sm mb-1">VoiceCore cost ({recommendedPlan})</div>
                  <div className="text-3xl font-bold text-amber-500">
                    ${planCost}
                    <span className="text-lg font-normal text-amber-500">/month</span>
                  </div>
                </div>

                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="text-green-400 text-sm mb-1">Your monthly ROI</div>
                  <div className="text-3xl font-bold text-green-500">
                    ${monthlySavings.toLocaleString()}
                    <span className="text-lg font-normal text-green-400">/month</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-zinc-800 rounded-lg p-4 text-center">
                    <TrendingUp className="w-6 h-6 text-amber-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-white">{yearlySavings.toLocaleString()}</div>
                    <div className="text-xs text-zinc-500">Yearly savings</div>
                  </div>
                  <div className="bg-zinc-800 rounded-lg p-4 text-center">
                    <Calendar className="w-6 h-6 text-amber-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-white">{paybackDays.toFixed(1)}</div>
                    <div className="text-xs text-zinc-500">Payback days</div>
                  </div>
                </div>

                <Link
                  href={`/signup?plan=${recommendedPlan}`}
                  className="block w-full bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold py-3 rounded-lg text-center transition"
                >
                  Get this ROI with 14-day free trial →
                </Link>
              </div>
            </div>
          </div>

          {/* Industry Breakdown */}
          <div className="mt-12 bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Industry Averages</h2>

            <div className="grid md:grid-cols-3 gap-4">
              {[
                { icon: '🦷', name: 'Dental', missRate: '28%', avgValue: '$250', description: 'New patient appointments' },
                { icon: '⚖️', name: 'Legal', missRate: '35%', avgValue: '$500', description: 'Case intake leads' },
                { icon: '🏠', name: 'Real Estate', missRate: '42%', avgValue: '$2,000', description: 'Showing requests' },
              ].map((ind, i) => (
                <div key={i} className="bg-zinc-800 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">{ind.icon}</span>
                    <span className="font-medium text-white">{ind.name}</span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Avg miss rate:</span>
                      <span className="text-white">{ind.missRate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Avg value:</span>
                      <span className="text-white">{ind.avgValue}</span>
                    </div>
                    <p className="text-zinc-500 text-xs mt-2">{ind.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <footer className="py-12 border-t border-zinc-800 mt-16">
        <div className="container mx-auto px-6 text-center">
          <p className="text-zinc-500 text-sm">
            © {new Date().getFullYear()} VoiceCore. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
