interface Agent {
  id: number
  name: string
  language: string
  voice_id: string | null
  is_active: boolean
  created_at: string
}

interface AgentCardProps {
  agent: Agent
  onToggle?: (id: number) => void
}

export default function AgentCard({ agent, onToggle }: AgentCardProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          agent.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
        }`}>
          {agent.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>
      
      <div className="space-y-2 mb-4">
        <p className="text-sm text-gray-500">
          <span className="font-medium">Language:</span> {agent.language}
        </p>
        {agent.voice_id && (
          <p className="text-sm text-gray-500">
            <span className="font-medium">Voice:</span> {agent.voice_id}
          </p>
        )}
        <p className="text-xs text-gray-400">
          Created: {new Date(agent.created_at).toLocaleDateString()}
        </p>
      </div>

      {onToggle && (
        <button
          onClick={() => onToggle(agent.id)}
          className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition ${
            agent.is_active 
              ? 'bg-red-50 text-red-600 hover:bg-red-100' 
              : 'bg-green-50 text-green-600 hover:bg-green-100'
          }`}
        >
          {agent.is_active ? 'Deactivate' : 'Activate'}
        </button>
      )}
    </div>
  )
}
