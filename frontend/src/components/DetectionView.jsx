import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  ShieldCheck,
  Zap,
  RotateCcw,
  Clock,
  Database,
  Sliders,
  AlertTriangle
} from 'lucide-react'

const DEFAULT_FEATURES = {
  duration: 0.0,
  protocol_type: 'tcp',
  service: 'http',
  flag: 'SF',
  src_bytes: 215.0,
  dst_bytes: 450.0,
  land: 0.0,
  wrong_fragment: 0.0,
  urgent: 0.0,
  hot: 0.0,
  num_failed_logins: 0.0,
  logged_in: 1.0,
  num_compromised: 0.0,
  root_shell: 0.0,
  su_attempted: 0.0,
  num_root: 0.0,
  num_file_creations: 0.0,
  num_shells: 0.0,
  num_access_files: 0.0,
  num_outbound_cmds: 0.0,
  is_host_login: 0.0,
  is_guest_login: 0.0,
  count: 1.0,
  srv_count: 1.0,
  serror_rate: 0.0,
  srv_serror_rate: 0.0,
  rerror_rate: 0.0,
  srv_rerror_rate: 0.0,
  same_srv_rate: 1.0,
  diff_srv_rate: 0.0,
  srv_diff_host_rate: 0.0,
  dst_host_count: 150.0,
  dst_host_srv_count: 255.0,
  dst_host_same_srv_rate: 1.0,
  dst_host_diff_srv_rate: 0.0,
  dst_host_same_src_port_rate: 0.05,
  dst_host_srv_diff_host_rate: 0.02,
  dst_host_serror_rate: 0.0,
  dst_host_srv_serror_rate: 0.0,
  dst_host_rerror_rate: 0.0,
  dst_host_srv_rerror_rate: 0.0,
  difficulty: 21.0
}

export default function DetectionView({ onPredictionComplete }) {
  const [task, setTask] = useState('five_class') // 'binary' or 'five_class'
  const [features, setFeatures] = useState(DEFAULT_FEATURES)
  const [presets, setPresets] = useState([])
  const [selectedPresetId, setSelectedPresetId] = useState('preset_normal_http')
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState(null)
  const [activeFormTab, setActiveFormTab] = useState('basic')

  // Load presets from backend on mount
  useEffect(() => {
    fetch('/api/presets')
      .then(res => res.json())
      .then(data => {
        setPresets(data)
        if (data.length > 0) {
          setFeatures(data[0].features)
        }
      })
      .catch(err => console.error('Failed to load presets:', err))
  }, [])

  const handlePresetSelect = (preset) => {
    setSelectedPresetId(preset.id)
    setFeatures({ ...DEFAULT_FEATURES, ...preset.features })
    setPrediction(null)
    setError(null)
  }

  const handleInputChange = (field, value, isNumeric = true) => {
    setFeatures(prev => ({
      ...prev,
      [field]: isNumeric ? (value === '' ? '' : parseFloat(value)) : value
    }))
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = task === 'binary' ? '/api/predict/binary' : '/api/predict/multiclass'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(features)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Prediction failed')
      }

      const result = await response.json()
      setPrediction(result)
      if (onPredictionComplete) {
        onPredictionComplete(result)
      }
    } catch (err) {
      console.error('Prediction error:', err)
      setError(err.message || 'Failed to execute inference')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFeatures(DEFAULT_FEATURES)
    setSelectedPresetId('')
    setPrediction(null)
    setError(null)
  }

  const getBadgeColor = (category) => {
    switch (category) {
      case 'Normal':
        return 'bg-emerald-50 text-emerald-700 border-emerald-300'
      case 'Attack':
      case 'DoS':
        return 'bg-rose-50 text-rose-700 border-rose-300'
      case 'Probe':
        return 'bg-amber-50 text-amber-700 border-amber-300'
      case 'R2L':
        return 'bg-purple-50 text-purple-700 border-purple-300'
      case 'U2R':
        return 'bg-indigo-50 text-indigo-700 border-indigo-300'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-300'
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Task Selector */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-[#6D28D9]" />
            <span>Interactive Intrusion Classification</span>
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Evaluate connection attributes using trained PySpark MLlib PipelineModels.
          </p>
        </div>

        {/* Binary vs 5-Class Toggle */}
        <div className="flex items-center space-x-1.5 bg-gray-100 p-1 rounded-lg border border-gray-200">
          <button
            onClick={() => { setTask('binary'); setPrediction(null); }}
            className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
              task === 'binary'
                ? 'bg-[#6D28D9] text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Binary (Normal vs Attack)
          </button>
          <button
            onClick={() => { setTask('five_class'); setPrediction(null); }}
            className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
              task === 'five_class'
                ? 'bg-[#6D28D9] text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Five-Class Taxonomy
          </button>
        </div>
      </div>

      {/* Preset Profiles Bar */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-gray-700 uppercase tracking-wider flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-[#6D28D9]" />
            <span>1-Click Benchmark Test Profiles:</span>
          </span>
          <span className="text-xs text-gray-500">From official NSL-KDD test sets</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          {presets.map((preset) => {
            const isSelected = selectedPresetId === preset.id
            return (
              <button
                key={preset.id}
                onClick={() => handlePresetSelect(preset)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  isSelected
                    ? 'bg-[#F5F3FF] border-[#6D28D9] shadow-sm ring-2 ring-[#6D28D9]/20'
                    : 'bg-white border-gray-200 hover:border-gray-300 hover:bg-gray-50/70 text-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${getBadgeColor(preset.category)}`}>
                    {preset.category}
                  </span>
                </div>
                <div className="text-xs font-semibold text-gray-900 mt-1.5 truncate">
                  {preset.name}
                </div>
                <p className="text-[10px] text-gray-500 truncate mt-0.5">
                  {preset.description}
                </p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Grid: Form Inputs (Left) and Prediction Output (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Feature Form (2 cols wide) */}
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-5">
          
          {/* Form Tabs */}
          <div className="flex border-b border-gray-200 space-x-2">
            <button
              onClick={() => setActiveFormTab('basic')}
              className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                activeFormTab === 'basic'
                  ? 'border-[#6D28D9] text-[#6D28D9]'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              1. Basic Connection
            </button>
            <button
              onClick={() => setActiveFormTab('content')}
              className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                activeFormTab === 'content'
                  ? 'border-[#6D28D9] text-[#6D28D9]'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              2. Content / Host
            </button>
            <button
              onClick={() => setActiveFormTab('traffic')}
              className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                activeFormTab === 'traffic'
                  ? 'border-[#6D28D9] text-[#6D28D9]'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              3. Time / Traffic
            </button>
            <button
              onClick={() => setActiveFormTab('dst_host')}
              className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                activeFormTab === 'dst_host'
                  ? 'border-[#6D28D9] text-[#6D28D9]'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              4. Destination Host
            </button>
          </div>

          {/* Tab 1: Basic Connection Attributes */}
          {activeFormTab === 'basic' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 text-xs">
              <div>
                <label className="block text-gray-600 font-medium mb-1">Protocol Type</label>
                <select
                  value={features.protocol_type}
                  onChange={(e) => handleInputChange('protocol_type', e.target.value, false)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                >
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                  <option value="icmp">ICMP</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Service</label>
                <input
                  type="text"
                  value={features.service}
                  onChange={(e) => handleInputChange('service', e.target.value, false)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                  placeholder="e.g. http, private, ftp"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Connection Flag</label>
                <select
                  value={features.flag}
                  onChange={(e) => handleInputChange('flag', e.target.value, false)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                >
                  <option value="SF">SF (Normal Established)</option>
                  <option value="S0">S0 (SYN without reply)</option>
                  <option value="REJ">REJ (Rejected Connection)</option>
                  <option value="RSTO">RSTO (Reset by Origin)</option>
                  <option value="RSTR">RSTR (Reset by Responder)</option>
                  <option value="SH">SH (SYN, FIN from Origin)</option>
                  <option value="S1">S1 (SYN exchange done)</option>
                  <option value="S2">S2 (SYN-ACK exchange)</option>
                  <option value="OTH">OTH (Other)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Duration (s)</label>
                <input
                  type="number"
                  value={features.duration}
                  onChange={(e) => handleInputChange('duration', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Source Bytes</label>
                <input
                  type="number"
                  value={features.src_bytes}
                  onChange={(e) => handleInputChange('src_bytes', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Destination Bytes</label>
                <input
                  type="number"
                  value={features.dst_bytes}
                  onChange={(e) => handleInputChange('dst_bytes', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Land (Same host/port)</label>
                <select
                  value={features.land}
                  onChange={(e) => handleInputChange('land', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                >
                  <option value="0">0 (No)</option>
                  <option value="1">1 (Yes)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Wrong Fragment</label>
                <input
                  type="number"
                  value={features.wrong_fragment}
                  onChange={(e) => handleInputChange('wrong_fragment', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Urgent Packets</label>
                <input
                  type="number"
                  value={features.urgent}
                  onChange={(e) => handleInputChange('urgent', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Tab 2: Content / Host Features */}
          {activeFormTab === 'content' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 text-xs">
              <div>
                <label className="block text-gray-600 font-medium mb-1">Logged In</label>
                <select
                  value={features.logged_in}
                  onChange={(e) => handleInputChange('logged_in', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                >
                  <option value="1">1 (Yes)</option>
                  <option value="0">0 (No)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Failed Logins</label>
                <input
                  type="number"
                  value={features.num_failed_logins}
                  onChange={(e) => handleInputChange('num_failed_logins', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Root Shell</label>
                <select
                  value={features.root_shell}
                  onChange={(e) => handleInputChange('root_shell', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                >
                  <option value="0">0 (No)</option>
                  <option value="1">1 (Yes)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Hot Indicators</label>
                <input
                  type="number"
                  value={features.hot}
                  onChange={(e) => handleInputChange('hot', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Num Compromised</label>
                <input
                  type="number"
                  value={features.num_compromised}
                  onChange={(e) => handleInputChange('num_compromised', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Su Attempted</label>
                <input
                  type="number"
                  value={features.su_attempted}
                  onChange={(e) => handleInputChange('su_attempted', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Num Root Accesses</label>
                <input
                  type="number"
                  value={features.num_root}
                  onChange={(e) => handleInputChange('num_root', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">File Creations</label>
                <input
                  type="number"
                  value={features.num_file_creations}
                  onChange={(e) => handleInputChange('num_file_creations', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Shell Prompts</label>
                <input
                  type="number"
                  value={features.num_shells}
                  onChange={(e) => handleInputChange('num_shells', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Tab 3: Time / Traffic Features */}
          {activeFormTab === 'traffic' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 text-xs">
              <div>
                <label className="block text-gray-600 font-medium mb-1">Count (Same host)</label>
                <input
                  type="number"
                  value={features.count}
                  onChange={(e) => handleInputChange('count', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Srv Count (Same srv)</label>
                <input
                  type="number"
                  value={features.srv_count}
                  onChange={(e) => handleInputChange('srv_count', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">SYN Error Rate (0-1)</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.serror_rate}
                  onChange={(e) => handleInputChange('serror_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">REJ Error Rate (0-1)</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.rerror_rate}
                  onChange={(e) => handleInputChange('rerror_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Same Service Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.same_srv_rate}
                  onChange={(e) => handleInputChange('same_srv_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Diff Service Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.diff_srv_rate}
                  onChange={(e) => handleInputChange('diff_srv_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Tab 4: Destination Host Features */}
          {activeFormTab === 'dst_host' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 text-xs">
              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host Count</label>
                <input
                  type="number"
                  value={features.dst_host_count}
                  onChange={(e) => handleInputChange('dst_host_count', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host Srv Count</label>
                <input
                  type="number"
                  value={features.dst_host_srv_count}
                  onChange={(e) => handleInputChange('dst_host_srv_count', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host Same Srv Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.dst_host_same_srv_rate}
                  onChange={(e) => handleInputChange('dst_host_same_srv_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host Diff Srv Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.dst_host_diff_srv_rate}
                  onChange={(e) => handleInputChange('dst_host_diff_srv_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host SYN Error Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.dst_host_serror_rate}
                  onChange={(e) => handleInputChange('dst_host_serror_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 font-medium mb-1">Dst Host REJ Error Rate</label>
                <input
                  type="number"
                  step="0.01"
                  value={features.dst_host_rerror_rate}
                  onChange={(e) => handleInputChange('dst_host_rerror_rate', e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-gray-900 focus:border-[#6D28D9] focus:ring-1 focus:ring-[#6D28D9] focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Form Action Buttons */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <button
              onClick={handleReset}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Features</span>
            </button>

            <button
              onClick={handlePredict}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-lg bg-[#6D28D9] hover:bg-[#5B21B6] text-white font-semibold text-sm transition-all shadow-sm shadow-purple-900/30 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Processing in Spark MLlib...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Execute MLlib Classification</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right Column: Prediction Output Card */}
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Inference Result
              </span>
              <span className="text-xs font-mono text-gray-500 bg-gray-50 px-2 py-0.5 rounded">
                {task === 'binary' ? 'Binary Decision Tree' : '5-Class Decision Tree'}
              </span>
            </div>

            {prediction ? (
              <div className="space-y-5">
                {/* Prediction Result Header */}
                <div className="text-center py-4 bg-[#F8F7FC] rounded-xl border border-gray-200">
                  <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-1">
                    Detected Classification
                  </div>
                  <div className={`inline-block text-2xl font-black px-5 py-1.5 rounded-xl border mt-1 shadow-sm ${getBadgeColor(prediction.predicted_class)}`}>
                    {prediction.predicted_class}
                  </div>
                  <div className="text-xs text-gray-600 mt-2">
                    Model Confidence: <strong className="text-gray-900 font-bold">{(prediction.confidence * 100).toFixed(2)}%</strong>
                  </div>
                </div>

                {/* Probability Distribution */}
                <div>
                  <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2.5">
                    Class Probabilities
                  </div>
                  <div className="space-y-2.5">
                    {Object.entries(prediction.probabilities || {}).map(([cls, prob]) => {
                      const pct = Math.round(prob * 100)
                      const isWinner = cls === prediction.predicted_class
                      return (
                        <div key={cls} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className={isWinner ? 'text-gray-900 font-bold' : 'text-gray-600'}>
                              {cls}
                            </span>
                            <span className="font-mono text-gray-600 font-medium">{pct}%</span>
                          </div>
                          <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                isWinner ? 'bg-[#6D28D9]' : 'bg-gray-300'
                              }`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Metadata Details */}
                <div className="pt-3 border-t border-gray-100 text-xs space-y-2 text-gray-600">
                  <div className="flex justify-between">
                    <span className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-gray-400" />
                      <span>Spark Inference Latency:</span>
                    </span>
                    <span className="font-mono text-gray-900 font-semibold">{prediction.inference_time_ms} ms</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="flex items-center space-x-1.5">
                      <Database className="w-3.5 h-3.5 text-gray-400" />
                      <span>Persistence Store:</span>
                    </span>
                    <span className="font-semibold text-[#6D28D9] uppercase bg-[#EDE9FE] px-2 py-0.5 rounded text-[11px]">
                      {prediction.storage_type === 'mongodb' ? 'MongoDB' : 'Fallback File'}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-gray-400 space-y-2">
                <ShieldCheck className="w-12 h-12 mx-auto text-gray-300 stroke-[1.5]" />
                <p className="text-sm font-semibold text-gray-700">Ready for Inference</p>
                <p className="text-xs text-gray-500 max-w-xs mx-auto">
                  Select a benchmark profile above or modify attributes and click Execute MLlib Classification.
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-500 text-center">
            Predictions are persisted immediately to the active history store.
          </div>
        </div>

      </div>
    </div>
  )
}
