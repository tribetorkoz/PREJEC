'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { X, Clock, AlertTriangle } from 'lucide-react';

interface TrialBannerProps {
  trialEndsAt?: string;
  daysRemaining?: number;
}

export default function TrialBanner({ trialEndsAt, daysRemaining }: TrialBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const [days, setDays] = useState(daysRemaining || 14);

  useEffect(() => {
    const dismissed = localStorage.getItem('trial_banner_dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const now = Date.now();
      if (now - dismissedTime < 24 * 60 * 60 * 1000) {
        setIsDismissed(true);
      } else {
        localStorage.removeItem('trial_banner_dismissed');
      }
    }
  }, []);

  const dismiss = () => {
    setIsDismissed(true);
    localStorage.setItem('trial_banner_dismissed', Date.now().toString());
  };

  if (isDismissed || daysRemaining === undefined || daysRemaining > 14) {
    return null;
  }

  const isUrgent = days <= 3;
  const progressPercent = (days / 14) * 100;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 ${
        isUrgent ? 'bg-amber-600' : 'bg-zinc-900 border-t border-zinc-800'
      }`}
    >
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            {isUrgent ? (
              <AlertTriangle className="w-5 h-5 text-white flex-shrink-0" />
            ) : (
              <Clock className="w-5 h-5 text-amber-500 flex-shrink-0" />
            )}
            
            <div className="flex-1">
              <p className={`font-medium ${isUrgent ? 'text-white' : 'text-white'}`}>
                {isUrgent ? (
                  <>Free Trial ending in <span className="font-bold">{days} day{days !== 1 ? 's' : ''}</span> — Upgrade to keep your agent live</>
                ) : (
                  <>Free Trial: <span className="font-bold text-amber-500">{days} day{days !== 1 ? 's' : ''}</span> remaining</>
                )}
              </p>
              
              <div className="mt-2 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    isUrgent ? 'bg-white' : 'bg-amber-500'
                  }`}
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Link
              href="/dashboard/billing"
              className={`font-semibold px-4 py-2 rounded-lg transition ${
                isUrgent
                  ? 'bg-white text-amber-600 hover:bg-zinc-100'
                  : 'bg-amber-500 text-zinc-950 hover:bg-amber-400'
              }`}
            >
              Upgrade Now
            </Link>
            
            <button
              onClick={dismiss}
              className="p-2 hover:bg-zinc-800 rounded-lg transition"
              title="Dismiss for 24 hours"
            >
              <X className={`w-5 h-5 ${isUrgent ? 'text-white' : 'text-zinc-400'}`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
