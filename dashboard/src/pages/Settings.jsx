import { useState } from 'react'

export default function Settings() {
    const [settings, setSettings] = useState({
        backendUrl: 'http://localhost:8000',
        wsUrl: 'ws://localhost:8000/ws/events',
        autoRefresh: true,
        refreshInterval: 5,
        notificationsEnabled: true,
        soundEnabled: false,
        severityThreshold: 3
    })

    const handleSave = () => {
        localStorage.setItem('safelift-settings', JSON.stringify(settings))
        alert('Settings saved successfully!')
    }

    const handleReset = () => {
        if (confirm('Reset all settings to defaults?')) {
            localStorage.removeItem('safelift-settings')
            window.location.reload()
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
                <p className="text-gray-600">Configure your SafeLift-AI dashboard</p>
            </div>

            <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Connection Settings</h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Backend API URL
                        </label>
                        <input
                            type="text"
                            value={settings.backendUrl}
                            onChange={(e) => setSettings({ ...settings, backendUrl: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                            placeholder="http://localhost:8000"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                            URL of the FastAPI backend server
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            WebSocket URL
                        </label>
                        <input
                            type="text"
                            value={settings.wsUrl}
                            onChange={(e) => setSettings({ ...settings, wsUrl: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                            placeholder="ws://localhost:8000/ws/events"
                        />
                        <p className="mt-1 text-xs text-gray-500">
                            WebSocket endpoint for real-time events
                        </p>
                    </div>
                </div>
            </div>

            <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Display Settings</h2>

                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <label className="text-sm font-medium text-gray-700">Auto Refresh</label>
                            <p className="text-xs text-gray-500">Automatically refresh event data</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.autoRefresh}
                                onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Refresh Interval (seconds)
                        </label>
                        <input
                            type="number"
                            min="1"
                            max="60"
                            value={settings.refreshInterval}
                            onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                    </div>
                </div>
            </div>

            <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Notification Settings</h2>

                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <label className="text-sm font-medium text-gray-700">Enable Notifications</label>
                            <p className="text-xs text-gray-500">Show browser notifications for new events</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.notificationsEnabled}
                                onChange={(e) => setSettings({ ...settings, notificationsEnabled: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div className="flex items-center justify-between">
                        <div>
                            <label className="text-sm font-medium text-gray-700">Sound Alerts</label>
                            <p className="text-xs text-gray-500">Play sound for critical events</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.soundEnabled}
                                onChange={(e) => setSettings({ ...settings, soundEnabled: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Notification Severity Threshold
                        </label>
                        <select
                            value={settings.severityThreshold}
                            onChange={(e) => setSettings({ ...settings, severityThreshold: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="1">All events (1+)</option>
                            <option value="2">Minor and above (2+)</option>
                            <option value="3">Moderate and above (3+)</option>
                            <option value="4">High and above (4+)</option>
                            <option value="5">Critical only (5)</option>
                        </select>
                        <p className="mt-1 text-xs text-gray-500">
                            Only show notifications for events at or above this severity
                        </p>
                    </div>
                </div>
            </div>

            <div className="flex gap-4">
                <button onClick={handleSave} className="btn-primary">
                    💾 Save Settings
                </button>

                <button onClick={handleReset} className="btn-secondary">
                    🔄 Reset to Defaults
                </button>
            </div>

            <div className="card bg-blue-50 border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Information</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Changes require page refresh to take effect</li>
                    <li>• Settings are stored in browser local storage</li>
                    <li>• Clear browser data to reset all settings</li>
                </ul>
            </div>
        </div>
    )
}
