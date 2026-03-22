'use client';

import { useState } from 'react';
import { Building2, ChevronRight, Loader2 } from 'lucide-react';

interface Step1CompanyProps {
  initialData?: any;
  onComplete: (data: any) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

const INDUSTRIES = [
  { value: 'dental', label: 'Dental Practice' },
  { value: 'legal', label: 'Legal Services' },
  { value: 'realty', label: 'Real Estate' },
  { value: 'medical', label: 'Medical Practice' },
  { value: 'auto', label: 'Auto Services' },
  { value: 'home', label: 'Home Services' },
  { value: 'retail', label: 'Retail' },
  { value: 'other', label: 'Other' },
];

const TIMEZONES = [
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Phoenix', label: 'Arizona Time' },
  { value: 'Europe/London', label: 'London (GMT)' },
  { value: 'Europe/Paris', label: 'Paris (CET)' },
  { value: 'Asia/Dubai', label: 'Dubai (GST)' },
  { value: 'Asia/Riyadh', label: 'Riyadh (AST)' },
  { value: 'Asia/Kolkata', label: 'India (IST)' },
];

export default function Step1Company({
  initialData,
  onComplete,
  loading,
  setLoading,
}: Step1CompanyProps) {
  const [formData, setFormData] = useState({
    company_name: initialData?.company_name || '',
    industry: initialData?.industry || '',
    phone: initialData?.phone || '',
    timezone: initialData?.timezone || 'America/New_York',
    website: initialData?.website || '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!formData.company_name.trim()) {
      setError('Company name is required');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/onboarding/step1/company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onComplete(data);
      } else {
        setError(data.detail || 'Failed to save company info');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Company Name <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          value={formData.company_name}
          onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          placeholder="Acme Dental Clinic"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Industry
        </label>
        <select
          value={formData.industry}
          onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        >
          <option value="">Select your industry</option>
          {INDUSTRIES.map((ind) => (
            <option key={ind.value} value={ind.value}>
              {ind.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Business Phone
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          placeholder="+1 (555) 123-4567"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Timezone
        </label>
        <select
          value={formData.timezone}
          onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        >
          {TIMEZONES.map((tz) => (
            <option key={tz.value} value={tz.value}>
              {tz.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Website
        </label>
        <input
          type="url"
          value={formData.website}
          onChange={(e) => setFormData({ ...formData, website: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          placeholder="https://yourcompany.com"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Saving...
          </>
        ) : (
          <>
            Continue
            <ChevronRight className="w-5 h-5" />
          </>
        )}
      </button>
    </form>
  );
}
