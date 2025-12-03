import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import LiveEvents from './pages/LiveEvents'
import History from './pages/History'
import Settings from './pages/Settings'

function App() {
    return (
        <Router>
            <div className="flex h-screen bg-gray-50">
                <Sidebar />

                <div className="flex-1 flex flex-col overflow-hidden">
                    <Topbar />

                    <main className="flex-1 overflow-y-auto p-6">
                        <Routes>
                            <Route path="/" element={<LiveEvents />} />
                            <Route path="/history" element={<History />} />
                            <Route path="/settings" element={<Settings />} />
                        </Routes>
                    </main>
                </div>
            </div>
        </Router>
    )
}

export default App
