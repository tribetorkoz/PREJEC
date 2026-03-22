'use client';

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Check, Loader2 } from 'lucide-react';

interface VoicePreviewProps {
  voiceId: string;
  voiceName: string;
  language?: string;
  gender?: string;
  isSelected?: boolean;
  onSelect?: (voiceId: string) => void;
}

export default function VoicePreview({
  voiceId,
  voiceName,
  language = 'en',
  gender,
  isSelected = false,
  onSelect,
}: VoicePreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const handlePreview = async () => {
    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/onboarding/step3/voice/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voiceId }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (audioRef.current) {
          audioRef.current.pause();
        }

        const audio = new Audio();
        audioRef.current = audio;
        
        audio.src = data.preview_url || `/api/v1/voice/preview/${voiceId}`;
        audio.onplay = () => setIsPlaying(true);
        audio.onended = () => {
          setIsPlaying(false);
          audioRef.current = null;
        };
        audio.onerror = () => {
          setIsPlaying(false);
          setIsLoading(false);
        };
        
        await audio.play();
        setIsLoading(false);
      } else {
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Failed to preview voice:', err);
      setIsLoading(false);
    }
  };

  const handleSelect = () => {
    if (onSelect) {
      onSelect(voiceId);
    }
  };

  return (
    <div
      className={`relative p-4 rounded-lg border transition-all ${
        isSelected
          ? 'border-amber-500 bg-amber-500/10'
          : 'border-zinc-700 hover:border-zinc-600 bg-zinc-800/50'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <button
            onClick={handleSelect}
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition ${
              isSelected
                ? 'border-amber-500 bg-amber-500'
                : 'border-zinc-600 hover:border-zinc-500'
            }`}
          >
            {isSelected && <Check className="w-4 h-4 text-zinc-950" />}
          </button>

          <div className="flex-1 min-w-0">
            <p className="text-white font-medium truncate">{voiceName}</p>
            <p className="text-zinc-500 text-sm">
              {language === 'en' ? 'English' : language}
              {gender && ` • ${gender}`}
            </p>
          </div>
        </div>

        <button
          onClick={handlePreview}
          disabled={isLoading}
          className={`p-3 rounded-full transition ${
            isPlaying
              ? 'bg-amber-500 text-zinc-950'
              : 'bg-zinc-700 text-zinc-300 hover:bg-zinc-600 hover:text-white'
          } disabled:opacity-50`}
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5" />
          )}
        </button>
      </div>

      {isPlaying && (
        <div className="mt-3">
          <div className="h-1 bg-zinc-700 rounded-full overflow-hidden">
            <div className="h-full bg-amber-500 rounded-full animate-pulse" style={{ width: '30%' }} />
          </div>
          <p className="text-xs text-zinc-500 mt-1 text-center">Playing preview...</p>
        </div>
      )}
    </div>
  );
}
