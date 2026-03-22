interface Call {
  id: number
  caller_phone: string
  duration_seconds: number | null
  transcript: string | null
  sentiment: string | null
  outcome: string | null
  created_at: string
}

interface CallLogProps {
  calls: Call[]
}

export default function CallLog({ calls }: CallLogProps) {
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  if (calls.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <p className="text-gray-500 text-center">No calls recorded yet</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sentiment</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Outcome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {calls.map(call => (
              <tr key={call.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900">{call.caller_phone}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{formatDuration(call.duration_seconds)}</td>
                <td className="px-6 py-4 text-sm">
                  {call.sentiment && (
                    <span className={`px-2 py-1 rounded text-xs ${
                      call.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                      call.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {call.sentiment}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{call.outcome || 'N/A'}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{formatDate(call.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
