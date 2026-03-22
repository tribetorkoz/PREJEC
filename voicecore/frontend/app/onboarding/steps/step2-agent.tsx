'use client';

import { useState } from 'react';
import { Bot, ChevronRight, Loader2 } from 'lucide-react';

interface Step2AgentProps {
  initialData?: any;
  onComplete: (data: any) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
  { value: 'fr', label: 'French' },
  { value: 'es', label: 'Spanish' },
  { value: 'de', label: 'German' },
  { value: 'auto', label: 'Auto-detect' },
];

const VERTICALS = [
  { value: 'dental', label: 'Dental Practice' },
  { value: 'legal', label: 'Legal Services' },
  { value: 'realty', label: 'Real Estate' },
  { value: 'medical', label: 'Medical Practice' },
  { value: 'auto', label: 'Auto Services' },
  { value: 'home', label: 'Home Services' },
  { value: 'retail', label: 'Retail' },
  { value: 'general', label: 'General Business' },
];

const DEFAULT_BUSINESS_HOURS = {
  monday: { open: '09:00', close: '18:00', enabled: true },
  tuesday: { open: '09:00', close: '18:00', enabled: true },
  wednesday: { open: '09:00', close: '18:00', enabled: true },
  thursday: { open: '09:00', close: '18:00', enabled: true },
  friday: { open: '09:00', close: '18:00', enabled: true },
  saturday: { open: '09:00', close: '17:00', enabled: false },
  sunday: { open: '09:00', close: '17:00', enabled: false },
};

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

export default function Step2Agent({
  initialData,
  onComplete,
  loading,
  setLoading,
}: Step2AgentProps) {
  const [formData, setFormData] = useState({
    agent_name: initialData?.agent_name || '',
    language: initialData?.language || 'en',
    business_hours: initialData?.business_hours || DEFAULT_BUSINESS_HOURS,
    custom_instructions: initialData?.custom_instructions || '',
    industry_vertical: initialData?.industry_vertical || '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!formData.agent_name.trim()) {
      setError('Agent name is required');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/onboarding/step2/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onComplete(data);
      } else {
        setError(data.detail || 'Failed to setup agent');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateBusinessHours = (day: string, field: string, value: any) => {
    setFormData({
      ...formData,
      business_hours: {
        ...formData.business_hours,
        [day]: {
          ...formData.business_hours[day],
          [field]: value,
        },
      },
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Agent Name <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          value={formData.agent_name}
          onChange={(e) => setFormData({ ...formData, agent_name: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          placeholder="Sarah, Alex, Max..."
          required
        />
        <p className="mt-1 text-xs text-zinc-500">
          This is how your AI receptionist will introduce itself
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Primary Language
        </label>
        <div className="grid grid-cols-3 gap-2">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.value}
              type="button"
              onClick={() => setFormData({ ...formData, language: lang.value })}
              className={`p-3 rounded-lg border text-center text-sm transition ${
                formData.language === lang.value
                  ? 'border-amber-500 bg-amber-500/10 text-amber-500'
                  : 'border-zinc-700 text-zinc-400 hover:border-zinc-600 hover:text-zinc-300'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Industry Vertical
        </label>
        <select
          value={formData.industry_vertical}
          onChange={(e) => setFormData({ ...formData, industry_vertical: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        >
          <option value="">Select industry (optional)</option>
          {VERTICALS.map((v) => (
            <option key={v.value} value={v.value}>
              {v.label}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-zinc-500">
          Selecting an industry helps your agent understand common questions
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Business Hours
        </label>
        <div className="space-y-2">
          {DAYS.map((day) => (
            <div key={day} className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => updateBusinessHours(day, 'enabled', !formData.business_hours[day].enabled)}
                className={`w-20 px-3 py-2 rounded-lg border text-sm font-medium transition ${
                  formData.business_hours[day].enabled
                    ? 'border-amber-500 bg-amber-500/10 text-amber-500'
                    : 'border-zinc-700 text-zinc-500'
                }`}
              >
                {day.charAt(0).toUpperCase() + day.slice(1, 3)}
              </button>
              {formData.business_hours[day].enabled ? (
                <div className="flex items-center gap-2 flex-1">
                  <input
                    type="time"
                    value={formData.business_hours[day].open}
                    onChange={(e) => updateBusinessHours(day, 'open', e.target.value)}
                    className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                  <span className="text-zinc-500">to</span>
                  <input
                    type="time"
                    value={formData.business_hours[day].close}
                    onChange={(e) => updateBusinessHours(day, 'close', e.target.value)}
                    className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              ) : (
                <span className="text-zinc-500 text-sm">Closed</span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Custom Instructions
        </label>
        <textarea
          value={formData.custom_instructions}
          onChange={(e) => setFormData({ ...formData, custom_instructions: e.target.value })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent h-32 resize-none"
          placeholder="Tell your agent how to handle specific situations..."
        />
        <p className="mt-1 text-xs text-zinc-500">
          Optional: Add special instructions for unique situations
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Setting up agent...
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
