'use client';

import { useState, useEffect, useCallback } from 'react';
import { Phone, Check, X, Loader2, Star, RefreshCw } from 'lucide-react';

type CallStatus = 'idle' | 'initiating' | 'ringing' | 'connected' | 'completed' | 'failed';

interface TestCallWidgetProps {
  companyNumber?: string;
  onStatusChange?: (status: CallStatus) => void;
  onComplete?: (rating: number) => void;
}

export default function TestCallWidget({
  companyNumber = '+1-XXX-XXX-XXXX',
  onStatusChange,
  onComplete,
}: TestCallWidgetProps) {
  const [testPhone, setTestPhone] = useState('');
  const [callStatus, setCallStatus] = useState<CallStatus>('idle');
  const [callSid, setCallSid] = useState<string | null>(null);
  const [rating, setRating] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [callDuration, setCallDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    onStatusChange?.(callStatus);
  }, [callStatus, onStatusChange]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (callStatus === 'connected') {
      interval = setInterval(() => {
        setCallDuration((d) => d + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [callStatus]);

  const startPollingStatus = useCallback((sid: string) => {
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
  }, []);

  const handleInitiateCall = async () => {
    setError(null);
    setCallDuration(0);

    if (!testPhone.trim()) {
      setError('Please enter your phone number');
      return;
    }

    if (!/^\+?[1-9]\d{6,14}$/.test(testPhone.replace(/\s/g, ''))) {
      setError('Please enter a valid phone number with country code');
      return;
    }

    setIsLoading(true);
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
        setError(data.detail || 'Failed to initiate call');
        setCallStatus('failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      setCallStatus('failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setCallStatus('idle');
    setCallSid(null);
    setError(null);
    setCallDuration(0);
    setRating(0);
  };

  const handleComplete = () => {
    onComplete?.(rating);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusIcon = () => {
    switch (callStatus) {
      case 'initiating':
        return <Loader2 className="w-16 h-16 text-amber-500 animate-spin" />;
      case 'ringing':
        return <Phone className="w-16 h-16 text-amber-500 animate-pulse" />;
      case 'connected':
        return (
          <div className="relative">
            <Phone className="w-16 h-16 text-green-500" />
            <div className="absolute inset-0 bg-green-500/20 rounded-full animate-ping" />
          </div>
        );
      case 'completed':
        return <Check className="w-16 h-16 text-green-500" />;
      case 'failed':
        return <X className="w-16 h-16 text-red-500" />;
      default:
        return <Phone className="w-16 h-16 text-zinc-500" />;
    }
  };

  const getStatusText = () => {
    switch (callStatus) {
      case 'initiating':
        return 'Initiating your call...';
      case 'ringing':
        return `Ringing ${testPhone}...`;
      case 'connected':
        return `Connected • ${formatDuration(callDuration)}`;
      case 'completed':
        return 'Call completed successfully!';
      case 'failed':
        return 'Call failed. Please try again.';
      default:
        return 'Ready to test your agent';
    }
  };

  const getStatusColor = () => {
    switch (callStatus) {
      case 'connected':
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-zinc-400';
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      <div className="text-center mb-6">
        <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-zinc-800 flex items-center justify-center">
          {getStatusIcon()}
        </div>
        <p className={`text-lg font-medium ${getStatusColor()}`}>{getStatusText()}</p>
        {callSid && <p className="text-zinc-600 text-sm mt-1">ID: {callSid}</p>}
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
              Enter the number that will receive the test call
            </p>
          </div>

          <button
            onClick={handleInitiateCall}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-amber-500 text-zinc-950 font-semibold rounded-lg hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? (
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
        <div className="space-y-6">
          <div className="text-center">
            <p className="text-zinc-300 mb-4">How was your experience?</p>
            <div className="flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 transition-transform hover:scale-110"
                >
                  <Star
                    className={`w-10 h-10 ${
                      star <= rating
                        ? 'fill-amber-500 text-amber-500'
                        : 'text-zinc-600 hover:text-zinc-500'
                    }`}
                  />
                </button>
              ))}
            </div>
            <p className="text-zinc-500 text-sm mt-2">
              {rating === 0 && 'Select a rating'}
              {rating === 1 && 'Poor - Needs improvement'}
              {rating === 2 && 'Fair - Some issues'}
              {rating === 3 && 'Good - Satisfactory'}
              {rating === 4 && 'Great - Very good'}
              {rating === 5 && 'Excellent - Perfect!'}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleRetry}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 transition"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
            <button
              onClick={handleComplete}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-400 transition"
            >
              <Check className="w-4 h-4" />
              {rating > 0 ? 'Submit & Continue' : 'Continue'}
            </button>
          </div>
        </div>
      )}

      {callStatus === 'failed' && (
        <div className="space-y-4">
          <button
            onClick={handleRetry}
            className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-zinc-700 text-white rounded-lg hover:bg-zinc-600 transition"
          >
            <RefreshCw className="w-5 h-5" />
            Try Again
          </button>
        </div>
      )}

      {error && (
        <p className="text-red-400 text-sm text-center mt-4">{error}</p>
      )}

      <div className="mt-6 pt-4 border-t border-zinc-800">
        <div className="flex items-center justify-between text-sm">
          <span className="text-zinc-500">Your agent will call from:</span>
          <span className="text-amber-500 font-medium">{companyNumber}</span>
        </div>
      </div>
    </div>
  );
}
