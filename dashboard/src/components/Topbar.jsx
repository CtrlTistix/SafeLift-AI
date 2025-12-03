import { useState, useEffect } from 'react'
import wsClient from '../utils/ws'

export default function Topbar() {
    const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED')
    const [currentTime, setCurrentTime] = useState(new Date())

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date())
            setConnectionStatus(wsClient.getConnectionState())
        }, 1000)

        return () => clearInterval(interval)
    }, [])

    const statusColors = {
        CONNECTED: 'bg-green-500',
        CONNECTING: 'bg-yellow-500',
        DISCONNECTED: 'bg-red-500',
        CLOSING: 'bg-orange-500',
        UNKNOWN: 'bg-gray-500'
    }

    const statusLabels = {
        CONNECTED: 'Connected',
        CONNECTING: 'Connecting...',
        DISCONNECTED: 'Disconnected',
        CLOSING: 'Closing...',
        UNKNOWN: 'Unknown'
    }

    return (
        <header className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
                    <p className="text-sm text-gray-500">Real-time forklift safety monitoring</p>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${statusColors[connectionStatus]} animate-pulse`}></div>
                        <span className="text-sm font-medium text-gray-700">
                            {statusLabels[connectionStatus]}
                        </span>
                    </div>

                    <div className="text-sm text-gray-600">
                        {currentTime.toLocaleTimeString()}
                    </div>
                </div>
            </div>
        </header>
    )
}
