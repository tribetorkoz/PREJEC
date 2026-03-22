'use client';

import { useState, useEffect } from 'react';
import { Phone, ChevronRight, Loader2, Check, Star, ArrowRight } from 'lucide-react';

interface Step5TestProps {
  onComplete: () => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

type CallStatus = 'idle' | 'initiating' | 'ringing' | 'connected' | 'completed' | 'failed';

export default function Step5Test({
  onComplete,
  loading,
  setLoading,
}: Step5TestProps) {
  const [testPhone, setTestPhone] = useState('');
  const [callStatus, setCallStatus] = useState<CallStatus>('idle');
  const [callSid, setCallSid] = useState<string | null>(null);
  const [rating, setRating] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleInitiateTestCall = async () => {
    setError(null);

    if (!testPhone.trim()) {
      setError('Please enter a phone number');
      return;
    }

    if (!/^\+?[1-9]\d{6,14}$/.test(testPhone.replace(/\s/g, ''))) {
      setError('Please enter a valid phone number with country code');
      return;
    }

    setLoading(true);
    setCallStatus('initiating');

    try {
      const response = await fetch('/api/v1/onboarding/step5/initiate-test-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_phone: testPhone }),
      });

      const data = await response.json();

      if (response.ok) {
        setCallSid(data.call_sid);
        setCallStatus('ringing');
        startPollingStatus(data.call_sid);
      } else {
        setError(data.detail || 'Failed to initiate test call');
        setCallStatus('failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      setCallStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  const startPollingStatus = (sid: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/onboarding/step5/test-call-status/${sid}`);
        const data = await response.json();

        if (data.status === 'in-progress') {
          setCallStatus('connected');
        } else if (data.status === 'completed') {
          setCallStatus('completed');
          clearInterval(pollInterval);
        } else if (data.status === 'failed') {
          setCallStatus('failed');
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Failed to poll call status');
      }
    }, 2000);
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/onboarding/step5/complete-onboarding', {
        method: 'POST',
      });

      if (response.ok) {
        onComplete();
      }
    } catch (err) {
      console.error('Failed to complete onboarding');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (callStatus) {
      case 'initiating':
        return <Loader2 className="w-12 h-12 text-amber-500 animate-spin" />;
      case 'ringing':
        return <Phone className="w-12 h-12 text-amber-500 animate-pulse" />;
      case 'connected':
        return <Check className="w-12 h-12 text-green-500" />;
      case 'completed':
        return <Check className="w-12 h-12 text-green-500" />;
      case 'failed':
        return <Phone className="w-12 h-12 text-red-500" />;
      default:
        return <Phone className="w-12 h-12 text-zinc-500" />;
    }
  };

  const getStatusText = () => {
    switch (callStatus) {
      case 'initiating':
        return 'Initiating call...';
      case 'ringing':
        return 'Ringing...';
      case 'connected':
        return 'Connected!';
      case 'completed':
        return 'Test call completed!';
      case 'failed':
        return 'Call failed';
      default:
        return 'Ready to test';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium text-white mb-2">
          Test Your AI Receptionist
        </h3>
        <p className="text-zinc-400 text-sm">
          Call your agent to see it in action before going live
        </p>
      </div>

      <div className="flex flex-col items-center justify-center py-8">
        <div className="w-24 h-24 bg-zinc-800 rounded-full flex items-center justify-center mb-4">
          {getStatusIcon()}
        </div>
        <p className="text-lg font-medium text-white mb-1">{getStatusText()}</p>
        {callSid && (
          <p className="text-zinc-500 text-sm">Call ID: {callSid}</p>
        )}
      </div>

      {callStatus === 'idle' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              Your Phone Number
            </label>
            <input
              type="tel"
              value={testPhone}
              onChange={(e) => setTestPhone(e.target.value)}
              placeholder="+1 (555) 123-4567"
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-zinc-500">
              Enter your phone number to receive the test call
            </p>
          </div>

          <button
            onClick={handleInitiateTestCall}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Starting...
              </>
            ) : (
              <>
                <Phone className="w-5 h-5" />
                Call Me Now
              </>
            )}
          </button>
        </div>
      )}

      {(callStatus === 'connected' || callStatus === 'completed') && (
        <div className="space-y-4">
          <div className="text-center">
            <p className="text-zinc-300 mb-2">How was the experience?</p>
            <div className="flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 transition"
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= rating
                        ? 'fill-amber-500 text-amber-500'
                        : 'text-zinc-600 hover:text-zinc-500'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleComplete}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Going live...
              </>
            ) : (
              <>
                Go Live
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      )}

      {callStatus === 'failed' && (
        <div className="space-y-4">
          <button
            onClick={() => setCallStatus('idle')}
            className="w-full px-6 py-3 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 transition"
          >
            Try Again
          </button>
        </div>
      )}

      {error && (
        <p className="text-red-400 text-sm text-center">{error}</p>
      )}
    </div>
  );
}
