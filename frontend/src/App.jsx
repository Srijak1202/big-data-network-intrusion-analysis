import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import HealthBanner from './components/HealthBanner'
import DashboardView from './components/DashboardView'
import DetectionView from './components/DetectionView'
import AnalyticsView from './components/AnalyticsView'
import EvaluationView from './components/EvaluationView'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [health, setHealth] = useState(null)

  const fetchHealth = () => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => {
        console.error('Failed to fetch health status:', err)
        setHealth({
          status: 'offline',
          spark_version: 'Offline',
          database: {
            status: 'offline_fallback',
            message: 'Cannot connect to API backend',
            total_records: 0
          }
        })
      })
  }

  useEffect(() => {
    fetchHealth()
    const timer = setInterval(fetchHealth, 15000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-[#F8F7FC] text-[#1F2937] flex flex-col font-sans selection:bg-[#6D28D9] selection:text-white">
      {/* Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
      />

      {/* Scope & Database Notice Banner */}
      <HealthBanner health={health} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'dashboard' && (
          <DashboardView setActiveTab={setActiveTab} />
        )}

        {activeTab === 'detection' && (
          <DetectionView onPredictionComplete={fetchHealth} />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsView />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationView />
        )}
      </main>

      {/* Project Footer */}
      <footer className="border-t border-gray-200 bg-white py-6 text-xs text-gray-500 text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            <strong className="text-gray-700">Review 3 Project</strong> • Big Data Analytics for Network Intrusion Detection
          </div>
          <div className="flex items-center space-x-3 text-gray-500">
            <span>Apache Spark 3.5</span>
            <span>•</span>
            <span>PySpark MLlib</span>
            <span>•</span>
            <span>FastAPI</span>
            <span>•</span>
            <span>React</span>
            <span>•</span>
            <span>MongoDB</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
