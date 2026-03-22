'use client';

import { useState, useEffect } from 'react';
import { Mic, ChevronRight, Loader2, Play, Pause, Check } from 'lucide-react';

interface Voice {
  voice_id: string;
  name: string;
  language: string;
  gender?: string;
}

interface Step3VoiceProps {
  initialData?: any;
  onComplete: (data: any) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export default function Step3Voice({
  initialData,
  onComplete,
  loading,
  setLoading,
}: Step3VoiceProps) {
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>(initialData?.voice_id || '');
  const [playingVoice, setPlayingVoice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fetchingVoices, setFetchingVoices] = useState(true);

  useEffect(() => {
    fetchVoices();
  }, []);

  const fetchVoices = async () => {
    setFetchingVoices(true);
    try {
      const response = await fetch('/api/v1/onboarding/step3/voices?language=en');
      if (response.ok) {
        const data = await response.json();
        setVoices(data);
      }
    } catch (err) {
      console.error('Failed to fetch voices:', err);
    } finally {
      setFetchingVoices(false);
    }
  };

  const handlePreview = async (voiceId: string) => {
    if (playingVoice === voiceId) {
      setPlayingVoice(null);
      return;
    }

    setPlayingVoice(voiceId);
    setTimeout(() => setPlayingVoice(null), 5000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedVoice) {
      setError('Please select a voice');
      return;
    }

    const selectedVoiceData = voices.find((v) => v.voice_id === selectedVoice);

    setLoading(true);
    try {
      const response = await fetch('/api/v1/onboarding/step3/voice/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voice_id: selectedVoice,
          voice_name: selectedVoiceData?.name || 'Unknown',
          voice_gender: selectedVoiceData?.gender || 'neutral',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onComplete(data);
      } else {
        setError(data.detail || 'Failed to select voice');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium text-white mb-2">
          Choose Your Agent&apos;s Voice
        </h3>
        <p className="text-zinc-400 text-sm">
          Select a voice that represents your brand
        </p>
      </div>

      {fetchingVoices ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {voices.map((voice) => (
            <button
              key={voice.voice_id}
              type="button"
              onClick={() => setSelectedVoice(voice.voice_id)}
              className={`w-full p-4 rounded-lg border transition ${
                selectedVoice === voice.voice_id
                  ? 'border-amber-500 bg-amber-500/10'
                  : 'border-zinc-700 hover:border-zinc-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {selectedVoice === voice.voice_id ? (
                    <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
                      <Check className="w-3 h-3 text-zinc-950" />
                    </div>
                  ) : (
                    <div className="w-5 h-5 border-2 border-zinc-600 rounded-full" />
                  )}
                  <div className="text-left">
                    <p className="text-white font-medium">{voice.name}</p>
                    <p className="text-zinc-500 text-sm">
                      {voice.language === 'en' ? 'English' : voice.language}
                      {voice.gender && ` • ${voice.gender}`}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePreview(voice.voice_id);
                  }}
                  className="p-2 rounded-full bg-zinc-800 hover:bg-zinc-700 transition"
                >
                  {playingVoice === voice.voice_id ? (
                    <Pause className="w-4 h-4 text-amber-500" />
                  ) : (
                    <Play className="w-4 h-4 text-zinc-400" />
                  )}
                </button>
              </div>
            </button>
          ))}
        </div>
      )}

      {error && (
        <p className="text-red-400 text-sm text-center">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading || !selectedVoice}
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
