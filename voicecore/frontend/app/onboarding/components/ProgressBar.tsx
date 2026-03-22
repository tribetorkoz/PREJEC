'use client';

import { Check } from 'lucide-react';

interface Step {
  id: number;
  title: string;
  icon: any;
  description: string;
}

interface ProgressBarProps {
  steps: Step[];
  currentStep: number;
}

export default function ProgressBar({ steps, currentStep }: ProgressBarProps) {
  return (
    <div className="flex items-center justify-between">
      {steps.map((step, index) => {
        const isCompleted = currentStep > step.id;
        const isCurrent = currentStep === step.id;
        const Icon = step.icon;

        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                  isCompleted
                    ? 'bg-amber-500 border-amber-500 text-zinc-950'
                    : isCurrent
                    ? 'border-amber-500 text-amber-500'
                    : 'border-zinc-700 text-zinc-500'
                }`}
              >
                {isCompleted ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}
              </div>
              <span
                className={`mt-2 text-xs font-medium hidden sm:block ${
                  isCompleted || isCurrent ? 'text-white' : 'text-zinc-500'
                }`}
              >
                {step.title}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-8 sm:w-16 h-0.5 mx-1 sm:mx-2 transition ${
                  isCompleted ? 'bg-amber-500' : 'bg-zinc-800'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
