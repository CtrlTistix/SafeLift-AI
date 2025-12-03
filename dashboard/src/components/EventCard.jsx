export default function EventCard({ event }) {
    const severityConfig = {
        1: { label: 'Low', color: 'bg-blue-100 text-blue-800 border-blue-300' },
        2: { label: 'Minor', color: 'bg-green-100 text-green-800 border-green-300' },
        3: { label: 'Moderate', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
        4: { label: 'High', color: 'bg-orange-100 text-orange-800 border-orange-300' },
        5: { label: 'Critical', color: 'bg-red-100 text-red-800 border-red-300' }
    }

    const config = severityConfig[event.severity] || severityConfig[3]

    const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp)
        return date.toLocaleString()
    }

    const eventTypeLabels = {
        'person_near_forklift': '⚠️ Person Near Forklift',
        'collision_risk': '🚨 Collision Risk',
        'speed_violation': '🏃 Speed Violation',
        'restricted_area': '🚫 Restricted Area'
    }

    return (
        <div className={`card border-l-4 ${config.color} hover:shadow-lg transition-shadow`}>
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">
                            {eventTypeLabels[event.type] || `📌 ${event.type}`}
                        </span>
                    </div>

                    <h3 className="font-semibold text-gray-900 text-lg mb-1">
                        {event.type.replace(/_/g, ' ').toUpperCase()}
                    </h3>

                    <p className="text-sm text-gray-600">
                        Source: <span className="font-medium">{event.source}</span>
                    </p>
                </div>

                <div className={`px-3 py-1 rounded-full text-xs font-bold ${config.color}`}>
                    {config.label}
                </div>
            </div>

            <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Timestamp:</span>
                    <span className="font-medium text-gray-700">{formatTimestamp(event.timestamp)}</span>
                </div>

                {event.metadata && Object.keys(event.metadata).length > 0 && (
                    <details className="mt-3">
                        <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                            View Details
                        </summary>
                        <div className="mt-2 p-3 bg-gray-50 rounded text-xs">
                            <pre className="whitespace-pre-wrap overflow-auto max-h-40">
                                {JSON.stringify(event.metadata, null, 2)}
                            </pre>
                        </div>
                    </details>
                )}
            </div>
        </div>
    )
}
