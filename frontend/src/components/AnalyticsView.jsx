import React, { useState, useEffect } from 'react'
import {
  BarChart2,
  ZoomIn,
  X,
  Maximize2
} from 'lucide-react'

export default function AnalyticsView() {
  const [catalog, setCatalog] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'eda', 'protocols', 'patterns', 'ml'
  const [selectedImage, setSelectedImage] = useState(null)
  const [rddSummary, setRddSummary] = useState(null)

  useEffect(() => {
    // Fetch visualization list
    fetch('/api/visualizations')
      .then(res => res.json())
      .then(data => {
        setCatalog(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load visualizations:', err)
        setLoading(false)
      })

    // Fetch Spark RDD summary
    fetch('/api/analytics/spark-rdd-summary')
      .then(res => res.json())
      .then(data => setRddSummary(data))
      .catch(err => console.error('Failed to load RDD summary:', err))
  }, [])

  const filterItems = (item) => {
    const fn = item.filename
    if (filter === 'all') return true
    if (filter === 'eda') {
      return fn.includes('category') || fn.includes('labels') || fn.includes('normal_vs_attack')
    }
    if (filter === 'protocols') {
      return fn.includes('protocol') || fn.includes('service') || fn.includes('flag')
    }
    if (filter === 'patterns') {
      return fn.includes('duration') || fn.includes('bytes') || fn.includes('error_rates') || fn.includes('correlation')
    }
    if (filter === 'ml') {
      return fn.includes('model_comparison') || fn.includes('confusion_matrix') || fn.includes('importance')
    }
    return true
  }

  const filteredCatalog = catalog.filter(filterItems)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
            <BarChart2 className="w-5 h-5 text-[#6D28D9]" />
            <span>Exploratory Data Analysis & Spark Analytics</span>
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Precomputed distributed aggregation charts produced by Apache Spark RDDs and Matplotlib.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap gap-1.5 bg-gray-100 p-1 rounded-lg border border-gray-200">
          {[
            { id: 'all', label: 'All Charts' },
            { id: 'eda', label: 'Attack Distributions' },
            { id: 'protocols', label: 'Protocols & Services' },
            { id: 'patterns', label: 'Traffic Patterns' },
            { id: 'ml', label: 'Model Evaluation' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                filter === tab.id
                  ? 'bg-[#6D28D9] text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Spark RDD Aggregation Highlights */}
      {rddSummary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:border-[#DDD6FE] transition-colors">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Total RDD Records</span>
            <div className="text-xl font-bold text-gray-900 mt-1">
              {rddSummary?.summary?.valid_records?.toLocaleString() || '125,973'}
            </div>
            <span className="text-[11px] text-gray-500">KDDTrain+ Dataset</span>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:border-[#DDD6FE] transition-colors">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">RDD Partitions</span>
            <div className="text-xl font-bold text-[#6D28D9] mt-1">
              {rddSummary?.summary?.rdd_partitions || '8 Partitions'}
            </div>
            <span className="text-[11px] text-gray-500">Custom Hash Partitioning</span>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:border-[#DDD6FE] transition-colors">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Distinct Services</span>
            <div className="text-xl font-bold text-[#6D28D9] mt-1">
              {rddSummary?.summary?.services || '70 Services'}
            </div>
            <span className="text-[11px] text-gray-500">http, private, smtp, etc.</span>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:border-[#DDD6FE] transition-colors">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Primary Protocol</span>
            <div className="text-xl font-bold text-emerald-700 mt-1">
              TCP (81.5%)
            </div>
            <span className="text-[11px] text-gray-500">102,689 TCP Connections</span>
          </div>
        </div>
      )}

      {/* Visualizations Grid */}
      {loading ? (
        <div className="py-20 text-center text-gray-500">
          <div className="w-8 h-8 border-2 border-[#6D28D9] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm">Loading analytics catalog...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCatalog.map((item, idx) => (
            <div
              key={idx}
              className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-[#DDD6FE] hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div className="p-3.5 border-b border-gray-100 flex items-center justify-between bg-white">
                <span className="text-xs font-bold text-gray-800 truncate pr-2">
                  {item.title}
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE]">
                  {item.category}
                </span>
              </div>

              {/* Chart Thumbnail with Hover Zoom */}
              <div
                className="relative bg-white p-3 cursor-pointer overflow-hidden flex items-center justify-center min-h-[220px]"
                onClick={() => setSelectedImage(item)}
              >
                <img
                  src={item.url}
                  alt={item.title}
                  className="max-h-56 object-contain rounded transition-transform duration-300 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-[#6D28D9]/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="bg-white/95 text-gray-900 text-xs font-semibold px-3.5 py-1.5 rounded-lg flex items-center space-x-1.5 shadow-md border border-gray-200">
                    <Maximize2 className="w-3.5 h-3.5 text-[#6D28D9]" />
                    <span>Click to Zoom</span>
                  </div>
                </div>
              </div>

              <div className="p-3 text-[11px] text-gray-500 bg-gray-50/70 border-t border-gray-100 flex justify-between items-center">
                <span className="font-mono text-gray-500 text-[10px]">{item.filename}</span>
                <button
                  onClick={() => setSelectedImage(item)}
                  className="text-[#6D28D9] hover:text-[#5B21B6] font-semibold flex items-center space-x-1"
                >
                  <ZoomIn className="w-3.5 h-3.5" />
                  <span>Inspect</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Zoom View */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div
            className="bg-white border border-gray-200 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div>
                <h3 className="font-bold text-gray-900 text-base">{selectedImage.title}</h3>
                <p className="text-xs text-gray-500 font-mono mt-0.5">{selectedImage.filename}</p>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="p-1.5 rounded-lg text-gray-500 hover:text-gray-800 hover:bg-gray-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 bg-white flex items-center justify-center overflow-auto flex-1">
              <img
                src={selectedImage.url}
                alt={selectedImage.title}
                className="max-h-[70vh] object-contain rounded"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
