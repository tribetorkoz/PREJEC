'use client';

import { useEffect, useState } from 'react';
import { adminRevenue, RevenueData } from '@/lib/admin-api';
import { DollarSign, TrendingUp, Users, Percent, PieChart } from 'lucide-react';

export default function RevenuePage() {
  const [data, setData] = useState<RevenueData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRevenue();
  }, []);

  const loadRevenue = async () => {
    try {
      const result = await adminRevenue.getData();
      setData(result);
    } catch (error) {
      console.error('Failed to load revenue:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-white">Revenue & Billing</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Monthly Recurring Revenue</p>
              <p className="text-2xl font-bold text-white mt-1">{formatCurrency(data?.mrr || 0)}</p>
            </div>
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Annual Recurring Revenue</p>
              <p className="text-2xl font-bold text-white mt-1">{formatCurrency(data?.arr || 0)}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Total Clients</p>
              <p className="text-2xl font-bold text-white mt-1">{data?.total_clients || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-zinc-400 text-sm">Avg Revenue Per User</p>
              <p className="text-2xl font-bold text-white mt-1">{formatCurrency(data?.arpu || 0)}</p>
            </div>
            <div className="w-12 h-12 bg-amber-500/10 rounded-lg flex items-center justify-center">
              <Percent className="w-6 h-6 text-amber-500" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Clients by Plan</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left p-4 text-zinc-400 font-medium">Plan</th>
                <th className="text-left p-4 text-zinc-400 font-medium">Clients</th>
                <th className="text-left p-4 text-zinc-400 font-medium">Price</th>
                <th className="text-left p-4 text-zinc-400 font-medium">Revenue</th>
                <th className="text-left p-4 text-zinc-400 font-medium">% of Total</th>
              </tr>
            </thead>
            <tbody>
              {data?.plans.map((plan) => (
                <tr key={plan.plan} className="border-b border-zinc-800">
                  <td className="p-4">
                    <span className="px-2 py-1 bg-zinc-800 text-zinc-300 text-sm rounded capitalize">
                      {plan.name}
                    </span>
                  </td>
                  <td className="p-4 text-white font-medium">{plan.count}</td>
                  <td className="p-4 text-zinc-300">{formatCurrency(plan.price)}/mo</td>
                  <td className="p-4 text-white font-medium">{formatCurrency(plan.revenue)}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-amber-500 rounded-full" 
                          style={{ width: `${plan.percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-zinc-400 text-sm">{plan.percentage}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
