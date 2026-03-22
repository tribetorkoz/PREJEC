'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Building2,
  Bot,
  Mic,
  Phone,
  Play,
  Check,
  ChevronRight,
  ChevronLeft,
  Loader2,
  ArrowRight,
} from 'lucide-react';

import Step1Company from './steps/step1-company';
import Step2Agent from './steps/step2-agent';
import Step3Voice from './steps/step3-voice';
import Step4Phone from './steps/step4-phone';
import Step5Test from './steps/step5-test';
import ProgressBar from './components/ProgressBar';

interface OnboardingState {
  current_step: number;
  completed: boolean;
  step1_data?: any;
  step2_data?: any;
  step3_data?: any;
  step4_data?: any;
  step5_data?: any;
}

const STEPS = [
  { id: 1, title: 'Company', icon: Building2, description: 'Business info' },
  { id: 2, title: 'Agent', icon: Bot, description: 'AI setup' },
  { id: 3, title: 'Voice', icon: Mic, description: 'Select voice' },
  { id: 4, title: 'Phone', icon: Phone, description: 'Get number' },
  { id: 5, title: 'Test', icon: Play, description: 'Test call' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [onboardingState, setOnboardingState] = useState<OnboardingState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOnboardingState();
  }, []);

  const fetchOnboardingState = async () => {
    try {
      const response = await fetch('/api/v1/onboarding/state');
      if (response.ok) {
        const data = await response.json();
        setOnboardingState(data);
        setCurrentStep(data.current_step || 1);
      }
    } catch (err) {
      console.error('Failed to fetch onboarding state:', err);
    }
  };

  const handleStepComplete = useCallback((step: number) => {
    if (step < 5) {
      setCurrentStep(step + 1);
      fetchOnboardingState();
    }
  }, []);

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    router.push('/dashboard');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1Company
            initialData={onboardingState?.step1_data}
            onComplete={(data) => handleStepComplete(1)}
            loading={loading}
            setLoading={setLoading}
          />
        );
      case 2:
        return (
          <Step2Agent
            initialData={onboardingState?.step2_data}
            onComplete={(data) => handleStepComplete(2)}
            loading={loading}
            setLoading={setLoading}
          />
        );
      case 3:
        return (
          <Step3Voice
            initialData={onboardingState?.step3_data}
            onComplete={(data) => handleStepComplete(3)}
            loading={loading}
            setLoading={setLoading}
          />
        );
      case 4:
        return (
          <Step4Phone
            initialData={onboardingState?.step4_data}
            onComplete={(data) => handleStepComplete(4)}
            loading={loading}
            setLoading={setLoading}
          />
        );
      case 5:
        return (
          <Step5Test
            onComplete={handleComplete}
            loading={loading}
            setLoading={setLoading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
                <Phone className="w-5 h-5 text-zinc-950" />
              </div>
              <span className="text-lg font-bold text-white">VoiceCore</span>
            </div>
            <span className="text-sm text-zinc-500">Setup your AI receptionist</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-3xl">
        <div className="mb-8">
          <ProgressBar steps={STEPS} currentStep={currentStep} />
        </div>

        <div className="mb-4">
          <h1 className="text-2xl font-bold text-white mb-1">
            {STEPS[currentStep - 1]?.title}
          </h1>
          <p className="text-zinc-400">
            Step {currentStep} of 5 — {STEPS[currentStep - 1]?.description}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 sm:p-8">
          {renderStep()}
        </div>

        <div className="flex items-center justify-between mt-6">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className="flex items-center gap-2 px-4 py-2 text-zinc-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>
          
          {currentStep === 1 && (
            <button
              onClick={() => handleStepComplete(1)}
              className="flex items-center gap-2 px-6 py-2 bg-zinc-800 text-zinc-400 rounded-lg hover:text-white hover:bg-zinc-700 transition"
            >
              Skip for now
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
