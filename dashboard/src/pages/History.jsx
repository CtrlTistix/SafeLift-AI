import { useState, useEffect } from 'react'
import EventCard from '../components/EventCard'
import api from '../utils/api'

export default function History() {
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [filters, setFilters] = useState({
        severity: 'all',
        type: 'all',
        limit: 50
    })

    const fetchEvents = async () => {
        setLoading(true)
        setError(null)

        try {
            const params = {
                limit: filters.limit
            }

            if (filters.severity !== 'all') {
                params.severity = filters.severity
            }

            if (filters.type !== 'all') {
                params.type = filters.type
            }

            const data = await api.getEvents(params)
            setEvents(data)
        } catch (err) {
            setError('Failed to load events. Please try again.')
            console.error('Error fetching events:', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchEvents()
    }, [filters])

    const uniqueTypes = [...new Set(events.map(e => e.type))]

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Event History</h1>
                <p className="text-gray-600">View and analyze past safety events</p>
            </div>

            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Severity
                        </label>
                        <select
                            value={filters.severity}
                            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
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

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Event Type
                        </label>
                        <select
                            value={filters.type}
                            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="all">All Types</option>
                            {uniqueTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Limit
                        </label>
                        <select
                            value={filters.limit}
                            onChange={(e) => setFilters({ ...filters, limit: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="25">25 events</option>
                            <option value="50">50 events</option>
                            <option value="100">100 events</option>
                            <option value="200">200 events</option>
                        </select>
                    </div>
                </div>

                <div className="mt-4 flex gap-2">
                    <button
                        onClick={fetchEvents}
                        className="btn-primary"
                    >
                        🔄 Refresh
                    </button>

                    <button
                        onClick={() => setFilters({ severity: 'all', type: 'all', limit: 50 })}
                        className="btn-secondary"
                    >
                        Clear Filters
                    </button>
                </div>
            </div>

            {loading && (
                <div className="card text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    <p className="mt-4 text-gray-600">Loading events...</p>
                </div>
            )}

            {error && (
                <div className="card bg-red-50 border border-red-200">
                    <p className="text-red-800">{error}</p>
                </div>
            )}

            {!loading && !error && (
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-900">
                            Events ({events.length})
                        </h2>
                    </div>

                    {events.length === 0 ? (
                        <div className="card text-center py-12">
                            <div className="text-6xl mb-4">📭</div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                No events found
                            </h3>
                            <p className="text-gray-600">
                                No events match your current filters
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {events.map((event) => (
                                <EventCard key={event.id} event={event} />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
