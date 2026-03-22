'use client';

import { useState, useEffect } from 'react';
import { Phone, ChevronRight, Loader2, Check, Search } from 'lucide-react';

interface PhoneNumber {
  phone_number: string;
  friendly_name?: string;
  monthly_cost: number;
  capabilities: string[];
}

interface Step4PhoneProps {
  initialData?: any;
  onComplete: (data: any) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export default function Step4Phone({
  initialData,
  onComplete,
  loading,
  setLoading,
}: Step4PhoneProps) {
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [selectedNumber, setSelectedNumber] = useState<string>(
    initialData?.phone_number || ''
  );
  const [areaCode, setAreaCode] = useState('');
  const [fetchingNumbers, setFetchingNumbers] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPhoneNumbers();
  }, []);

  const fetchPhoneNumbers = async (areaCodeFilter?: string) => {
    setFetchingNumbers(true);
    try {
      const url = areaCodeFilter
        ? `/api/v1/onboarding/step4/available-numbers?area_code=${areaCodeFilter}`
        : '/api/v1/onboarding/step4/available-numbers';
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setPhoneNumbers(data);
      }
    } catch (err) {
      console.error('Failed to fetch phone numbers:', err);
    } finally {
      setFetchingNumbers(false);
    }
  };

  const handleSearch = () => {
    fetchPhoneNumbers(areaCode);
  };

  const handleProvision = async () => {
    setError(null);

    if (!selectedNumber) {
      setError('Please select a phone number');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/onboarding/step4/provision-number', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: selectedNumber,
          country: 'US',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onComplete(data);
      } else {
        setError(data.detail || 'Failed to provision phone number');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium text-white mb-2">
          Get Your Business Phone Number
        </h3>
        <p className="text-zinc-400 text-sm">
          This number will be answered by your AI receptionist
        </p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={areaCode}
            onChange={(e) => setAreaCode(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search by area code (e.g., 212)"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={fetchingNumbers}
          className="px-4 py-3 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 disabled:opacity-50 transition"
        >
          {fetchingNumbers ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            'Search'
          )}
        </button>
      </div>

      <div className="space-y-2 max-h-72 overflow-y-auto">
        {phoneNumbers.length === 0 && !fetchingNumbers && (
          <p className="text-center text-zinc-500 py-8">
            No phone numbers available
          </p>
        )}
        {phoneNumbers.map((num) => (
          <button
            key={num.phone_number}
            type="button"
            onClick={() => setSelectedNumber(num.phone_number)}
            className={`w-full p-4 rounded-lg border transition ${
              selectedNumber === num.phone_number
                ? 'border-amber-500 bg-amber-500/10'
                : 'border-zinc-700 hover:border-zinc-600'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {selectedNumber === num.phone_number ? (
                  <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-zinc-950" />
                  </div>
                ) : (
                  <div className="w-5 h-5 border-2 border-zinc-600 rounded-full" />
                )}
                <div className="text-left">
                  <p className="text-white font-medium">{num.phone_number}</p>
                  <p className="text-zinc-500 text-sm">
                    {num.friendly_name || 'Local number'}
                  </p>
                </div>
              </div>
              <span className="text-amber-500 font-medium">
                ${num.monthly_cost}/mo
              </span>
            </div>
          </button>
        ))}
      </div>

      {error && (
        <p className="text-red-400 text-sm text-center">{error}</p>
      )}

      <button
        onClick={handleProvision}
        disabled={loading || !selectedNumber}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Provisioning...
          </>
        ) : (
          <>
            Continue
            <ChevronRight className="w-5 h-5" />
          </>
        )}
      </button>
    </div>
  );
}
