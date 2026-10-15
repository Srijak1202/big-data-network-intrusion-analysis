import React from 'react'
import { Shield, Activity, BarChart3, Award, Database, Cpu } from 'lucide-react'

export default function Navbar({ activeTab, setActiveTab, health }) {
  const isMongoConnected = health?.database?.status === 'connected'
  const isSparkHealthy = health?.status === 'healthy'

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Project Title */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-[#EDE9FE] border border-[#DDD6FE] rounded-lg text-[#6D28D9]">
              <Shield className="w-6 h-6 text-[#6D28D9]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-gray-900">NIDS</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE]">
                  Review 3
                </span>
              </div>
              <p className="text-xs text-gray-500 hidden sm:block">
                Big Data Analytics & PySpark MLlib Pipeline
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1.5">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE] shadow-sm font-semibold'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Cpu className={`w-4 h-4 ${activeTab === 'dashboard' ? 'text-[#6D28D9]' : 'text-gray-500'}`} />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('detection')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'detection'
                  ? 'bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE] shadow-sm font-semibold'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Activity className={`w-4 h-4 ${activeTab === 'detection' ? 'text-[#6D28D9]' : 'text-gray-500'}`} />
              <span>Intrusion Detection</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'analytics'
                  ? 'bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE] shadow-sm font-semibold'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <BarChart3 className={`w-4 h-4 ${activeTab === 'analytics' ? 'text-[#6D28D9]' : 'text-gray-500'}`} />
              <span>EDA & Visualizations</span>
            </button>

            <button
              onClick={() => setActiveTab('evaluation')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'evaluation'
                  ? 'bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE] shadow-sm font-semibold'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Award className={`w-4 h-4 ${activeTab === 'evaluation' ? 'text-[#6D28D9]' : 'text-gray-500'}`} />
              <span>Model Evaluation & History</span>
            </button>
          </nav>

          {/* System Status Indicators */}
          <div className="flex items-center space-x-2.5">
            {/* Spark Indicator */}
            <div
              title={`Apache Spark Engine: ${isSparkHealthy ? 'Operational' : 'Degraded'}`}
              className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-50 border border-gray-200 text-gray-700"
            >
              <span className={`w-2 h-2 rounded-full ${isSparkHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              <span className="hidden lg:inline">Spark 3.5</span>
            </div>

            {/* DB Indicator */}
            <div
              title={health?.database?.message || 'Database status'}
              className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-50 border border-gray-200 text-gray-700"
            >
              <Database className={`w-3.5 h-3.5 ${isMongoConnected ? 'text-emerald-600' : 'text-amber-600'}`} />
              <span className="hidden lg:inline">
                {isMongoConnected ? 'MongoDB' : 'Fallback Store'}
              </span>
            </div>
          </div>

        </div>
      </div>

      {/* Mobile navigation bar */}
      <div className="flex md:hidden border-t border-gray-200 bg-white overflow-x-auto py-1.5 px-3 space-x-1.5">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-3 py-1.5 text-xs rounded-md shrink-0 font-medium ${
            activeTab === 'dashboard'
              ? 'bg-[#EDE9FE] text-[#6D28D9] font-semibold'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Dashboard
        </button>
        <button
          onClick={() => setActiveTab('detection')}
          className={`px-3 py-1.5 text-xs rounded-md shrink-0 font-medium ${
            activeTab === 'detection'
              ? 'bg-[#EDE9FE] text-[#6D28D9] font-semibold'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Detection
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-3 py-1.5 text-xs rounded-md shrink-0 font-medium ${
            activeTab === 'analytics'
              ? 'bg-[#EDE9FE] text-[#6D28D9] font-semibold'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          EDA
        </button>
        <button
          onClick={() => setActiveTab('evaluation')}
          className={`px-3 py-1.5 text-xs rounded-md shrink-0 font-medium ${
            activeTab === 'evaluation'
              ? 'bg-[#EDE9FE] text-[#6D28D9] font-semibold'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Evaluation
        </button>
      </div>
    </header>
  )
}
