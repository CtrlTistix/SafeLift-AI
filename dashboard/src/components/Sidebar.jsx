import { Link, useLocation } from 'react-router-dom'

const navigation = [
    { name: 'Live Events', path: '/', icon: '🔴' },
    { name: 'History', path: '/history', icon: '📊' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
]

export default function Sidebar() {
    const location = useLocation()

    return (
        <div className="w-64 bg-gray-900 text-white flex flex-col">
            <div className="p-6 border-b border-gray-700">
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <span className="text-3xl">🏗️</span>
                    SafeLift-AI
                </h1>
                <p className="text-gray-400 text-sm mt-1">Safety Monitoring</p>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.path

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${isActive
                                    ? 'bg-primary-600 text-white'
                                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                                }
              `}
                        >
                            <span className="text-xl">{item.icon}</span>
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    )
                })}
            </nav>

            <div className="p-4 border-t border-gray-700">
                <div className="text-xs text-gray-400">
                    <p>Version 1.0.0</p>
                    <p className="mt-1">SafeLift-AI Dashboard</p>
                </div>
            </div>
        </div>
    )
}
