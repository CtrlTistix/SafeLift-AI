import { useState, useEffect } from 'react'
import EventCard from '../components/EventCard'
import wsClient from '../utils/ws'

export default function LiveEvents() {
    const [events, setEvents] = useState([])
    const [filter, setFilter] = useState({ severity: 'all', type: 'all' })

    useEffect(() => {
        wsClient.connect()

        const unsubscribe = wsClient.subscribe((newEvent) => {
            setEvents(prevEvents => [newEvent, ...prevEvents].slice(0, 50))
        })

        return () => {
            unsubscribe()
        }
    }, [])

    const filteredEvents = events.filter(event => {
        if (filter.severity !== 'all' && event.severity !== parseInt(filter.severity)) {
            return false
        }
        if (filter.type !== 'all' && event.type !== filter.type) {
            return false
        }
        return true
    })

    const uniqueTypes = [...new Set(events.map(e => e.type))]

    const severityCounts = events.reduce((acc, event) => {
        acc[event.severity] = (acc[event.severity] || 0) + 1
        return acc
    }, {})

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Live Events</h1>
                <p className="text-gray-600">Real-time safety event monitoring</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {[1, 2, 3, 4, 5].map(severity => (
                    <div key={severity} className="card text-center">
                        <div className="text-2xl font-bold text-gray-900">{severityCounts[severity] || 0}</div>
                        <div className="text-sm text-gray-600">Level {severity}</div>
                    </div>
                ))}
            </div>

            <div className="card">
                <div className="flex gap-4 items-center">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Filter by Severity
                        </label>
                        <select
                            value={filter.severity}
                            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="all">All Severities</option>
                            <option value="5">Critical (5)</option>
                            <option value="4">High (4)</option>
                            <option value="3">Moderate (3)</option>
                            <option value="2">Minor (2)</option>
                            <option value="1">Low (1)</option>
                        </select>
                    </div>

                    <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Filter by Type
                        </label>
                        <select
                            value={filter.type}
                            onChange={(e) => setFilter({ ...filter, type: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="all">All Types</option>
                            {uniqueTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-1 flex items-end">
                        <button
                            onClick={() => setFilter({ severity: 'all', type: 'all' })}
                            className="btn-secondary w-full"
                        >
                            Clear Filters
                        </button>
                    </div>
                </div>
            </div>

            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Recent Events ({filteredEvents.length})
                    </h2>

                    {events.length > 0 && (
                        <button
                            onClick={() => setEvents([])}
                            className="text-sm text-red-600 hover:text-red-700 font-medium"
                        >
                            Clear All
                        </button>
                    )}
                </div>

                {filteredEvents.length === 0 ? (
                    <div className="card text-center py-12">
                        <div className="text-6xl mb-4">👀</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                            No events yet
                        </h3>
                        <p className="text-gray-600">
                            Waiting for real-time events from the vision module...
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {filteredEvents.map((event, index) => (
                            <EventCard key={event.id || index} event={event} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
