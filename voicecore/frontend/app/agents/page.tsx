'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  Clock, ChevronDown, Volume2, Check, X, Loader2
} from 'lucide-react'
import { api } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface Agent {
  id: number
  name: string
  language: string
  voice_id: string | null
  system_prompt: string | null
  is_active: boolean
}

const languages = [
  { code: 'auto', name: 'Auto-detect' },
  { code: 'en', name: 'English' },
  { code: 'ar', name: 'Arabic / العربية' },
  { code: 'fr', name: 'French / Français' },
  { code: 'es', name: 'Spanish / Español' },
]

const voices = [
  { id: 'rachel', name: 'Rachel (Female)', preview: '🔊' },
  { id: 'josh', name: 'Josh (Male)', preview: '🔊' },
  { id: 'adam', name: 'Adam (Male)', preview: '🔊' },
  { id: 'sarah', name: 'Sarah (Female)', preview: '🔊' },
]

const businessHours = [
  { day: 'Monday', start: '09:00', end: '18:00', enabled: true },
  { day: 'Tuesday', start: '09:00', end: '18:00', enabled: true },
  { day: 'Wednesday', start: '09:00', end: '18:00', enabled: true },
  { day: 'Thursday', start: '09:00', end: '18:00', enabled: true },
  { day: 'Friday', start: '09:00', end: '18:00', enabled: true },
  { day: 'Saturday', start: '10:00', end: '14:00', enabled: false },
  { day: 'Sunday', start: '10:00', end: '14:00', enabled: false },
]

export default function AgentsPage() {
  const { user, loading: authLoading } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agent, setAgent] = useState<Agent | null>(null);
  
  const [prompt, setPrompt] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('rachel')
  const [showVoiceDropdown, setShowVoiceDropdown] = useState(false)
  const [hours, setHours] = useState(businessHours)
  const [isTesting, setIsTesting] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAgents = async () => {
      if (!user) return;
      try {
        const res = await api.agents.list(user.company_id);
        setAgents(res.data);
        if (res.data.length > 0) {
          const firstAgent = res.data[0];
          setAgent(firstAgent);
          setPrompt(firstAgent.system_prompt || '');
          setSelectedVoice(firstAgent.voice_id || 'rachel');
        }
      } catch (err) {
        console.error('Error fetching agents:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, [user]);

  const handleSave = async () => {
    if (!agent || !user) return;
    try {
      setSaved(true);
      await api.agents.update(agent.id, {
        system_prompt: prompt,
        voice_id: selectedVoice,
        name: agent.name,
        language: agent.language
      });
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      console.error('Error saving agent', err);
      setSaved(false);
    }
  }

  const handleTestCall = () => {
    setIsTesting(true)
    setTimeout(() => setIsTesting(false), 3000)
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground">Loading your agents...</p>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center space-y-4">
        <p className="text-muted-foreground text-lg">No agents found for your company.</p>
        <button className="btn-primary">Create New Agent</button>
      </div>
    )
  }

  const toggleHour = (day: string) => {
    setHours(hours.map(h => 
      h.day === day ? { ...h, enabled: !h.enabled } : h
    ))
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border glass sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Phone className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground">VoiceCore</span>
            </Link>
            <div className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition">Dashboard</Link>
              <Link href="/agents" className="text-primary font-medium">Agents</Link>
              <Link href="/calls" className="text-muted-foreground hover:text-foreground transition">Calls</Link>
              <Link href="/analytics" className="text-muted-foreground hover:text-foreground transition">Analytics</Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Agent Configuration</h1>
            <p className="text-muted-foreground">Customize your AI voice agent</p>
          </div>
          <button 
            onClick={handleTestCall}
            disabled={isTesting}
            className="btn-primary flex items-center gap-2"
          >
            <Play className={`w-4 h-4 ${isTesting ? 'animate-pulse' : ''}`} />
            {isTesting ? 'Connecting...' : 'Test Call'}
          </button>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center gap-2">
                <Settings className="w-5 h-5 text-primary" />
                Basic Settings
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-foreground font-medium mb-2">Agent Name</label>
                  <input
                    type="text"
                    value={agent.name}
                    onChange={(e) => setAgent({...agent, name: e.target.value})}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-foreground font-medium mb-2">
                    <Globe className="w-4 h-4 inline mr-2" />
                    Language
                  </label>
                  <select
                    value={agent.language}
                    onChange={(e) => setAgent({...agent, language: e.target.value})}
                    className="input-field w-full"
                  >
                    {languages.map(lang => (
                      <option key={lang.code} value={lang.code}>{lang.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-foreground font-medium mb-2">
                    <Volume2 className="w-4 h-4 inline mr-2" />
                    Voice
                  </label>
                  <div className="relative">
                    <button
                      onClick={() => setShowVoiceDropdown(!showVoiceDropdown)}
                      className="input-field w-full flex items-center justify-between"
                    >
                      <span>{voices.find(v => v.id === selectedVoice)?.name}</span>
                      <ChevronDown className="w-4 h-4" />
                    </button>
                    {showVoiceDropdown && (
                      <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-10">
                        {voices.map(voice => (
                          <button
                            key={voice.id}
                            onClick={() => {
                              setSelectedVoice(voice.id)
                              setShowVoiceDropdown(false)
                            }}
                            className={`w-full px-4 py-3 text-left hover:bg-secondary flex items-center justify-between ${
                              selectedVoice === voice.id ? 'text-primary' : 'text-foreground'
                            }`}
                          >
                            <span>{voice.name}</span>
                            {selectedVoice === voice.id && <Check className="w-4 h-4" />}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary" />
                Business Hours
              </h2>
              
              <div className="space-y-3">
                {hours.map(hour => (
                  <div key={hour.day} className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => toggleHour(hour.day)}
                        className={`w-10 h-6 rounded-full transition-colors ${
                          hour.enabled ? 'bg-primary' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          hour.enabled ? 'translate-x-5' : 'translate-x-1'
                        }`} />
                      </button>
                      <span className="text-foreground">{hour.day}</span>
                    </div>
                    {hour.enabled && (
                      <span className="text-muted-foreground">{hour.start} - {hour.end}</span>
                    )}
                    {!hour.enabled && <span className="text-muted-foreground">Closed</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5 text-primary" />
                Agent Personality
              </h2>
              <p className="text-muted-foreground mb-4">Define how your AI agent behaves.</p>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={10}
                className="input-field w-full resize-none"
                placeholder="Enter your agent's system prompt..."
              />
              <div className="mt-4 flex items-center justify-between">
                <span className="text-muted-foreground text-sm">{prompt.length} characters</span>
                <button onClick={handleSave} className="btn-primary flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  {saved ? 'Saved!' : 'Save Changes'}
                </button>
              </div>
            </div>

            <div className="card p-6">
              <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-primary" />
                Knowledge Base
              </h2>
              <p className="text-muted-foreground mb-4">Upload company documents to help your agent.</p>
              
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-foreground mb-2">Drop files here or click to upload</p>
                <p className="text-muted-foreground text-sm">PDF, TXT, or DOCX (max 10MB)</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
