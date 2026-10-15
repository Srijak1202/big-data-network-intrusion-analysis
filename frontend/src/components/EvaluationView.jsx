import React, { useState, useEffect } from 'react'
import {
  Award,
  AlertTriangle,
  Database,
  Trash2,
  RefreshCw,
  TrendingUp,
  Sliders,
  CheckCircle2,
  Clock,
  Layers,
  FileText
} from 'lucide-react'

export default function EvaluationView() {
  const [modelComparison, setModelComparison] = useState(null)
  const [testMetrics, setTestMetrics] = useState(null)
  const [featureImportance, setFeatureImportance] = useState(null)
  const [historyData, setHistoryData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('metrics') // 'metrics' or 'history'

  const fetchData = () => {
    setLoading(true)
    Promise.all([
      fetch('/api/analytics/model-comparison').then(r => r.json()),
      fetch('/api/analytics/test-metrics').then(r => r.json()),
      fetch('/api/analytics/feature-importance').then(r => r.json()),
      fetch('/api/history').then(r => r.json()),
    ])
      .then(([comp, metrics, imp, hist]) => {
        setModelComparison(comp)
        setTestMetrics(metrics)
        setFeatureImportance(imp)
        setHistoryData(hist)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load evaluation data:', err)
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear the prediction history?')) return
    setHistoryLoading(true)
    try {
      await fetch('/api/history', { method: 'DELETE' })
      const res = await fetch('/api/history').then(r => r.json())
      setHistoryData(res)
    } catch (err) {
      console.error('Failed to clear history:', err)
    } finally {
      setHistoryLoading(false)
    }
  }

  const getBadgeClass = (category) => {
    switch (category) {
      case 'Normal':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'Attack':
      case 'DoS':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'Probe':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      case 'R2L':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'U2R':
        return 'bg-orange-50 text-orange-700 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header and Sub-Tab Navigation */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
            <Award className="w-5 h-5 text-[#6D28D9]" />
            <span>Model Evaluation &amp; Prediction History</span>
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Verified ground-truth metrics on NSL-KDD held-out test benchmark and live prediction audit log.
          </p>
        </div>

        <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200">
          <button
            onClick={() => setActiveTab('metrics')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
              activeTab === 'metrics'
                ? 'bg-[#6D28D9] text-white shadow-sm'
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Review 3 Evaluation Metrics
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
              activeTab === 'history'
                ? 'bg-[#6D28D9] text-white shadow-sm'
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Prediction History ({historyData?.count || 0})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-gray-400">
          <div className="w-8 h-8 border-2 border-[#6D28D9] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm">Loading evaluation metrics...</p>
        </div>
      ) : activeTab === 'metrics' ? (
        <div className="space-y-6">

          {/* CRITICAL BENCHMARK ALERT CALLOUT — visible amber on white */}
          <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 text-xs leading-relaxed">
            <div className="flex items-start space-x-2.5">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-amber-900 block text-sm mb-1 font-semibold">
                  Official NSL-KDD Benchmark Evaluation &amp; Zero-Day Behavior
                </strong>
                <span className="text-amber-800">
                  The models were trained on{' '}
                  <code className="text-amber-700 bg-amber-100 px-1 rounded font-mono">KDDTrain+.txt</code>{' '}
                  (125,973 records) with model selection performed using 80/20 validation Macro-F1. The test
                  metrics shown below were computed once on the official held-out{' '}
                  <code className="text-amber-700 bg-amber-100 px-1 rounded font-mono">KDDTest+.txt</code>{' '}
                  benchmark (22,544 records).
                </span>
                <p className="mt-1.5 text-amber-800">
                  <strong>Notice on R2L and U2R Recall:</strong> The NSL-KDD test set intentionally introduces
                  17 novel attack types (e.g.,{' '}
                  <em>snmpguess, httptunnel, ps, sqlattack</em>) that never appeared in the training set. This
                  accounts for the expected lower recall on R2L (8.35%) and U2R (16.42%) while preserving high
                  precision and robust overall accuracy.
                </p>
              </div>
            </div>
          </div>

          {/* Summary Metric Cards: Validation vs Test */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Binary Model Card */}
            <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center border-b border-gray-100 pb-3">
                <span className="font-bold text-gray-900 text-base">Binary Detection (Normal vs Attack)</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                  Winner: Decision Tree
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-[#EDE9FE] rounded-lg border border-purple-200">
                  <span className="text-gray-500 block text-[11px] uppercase tracking-wider">Validation Macro-F1</span>
                  <span className="text-xl font-bold text-emerald-600 mt-1 block">99.72%</span>
                  <span className="text-[10px] text-gray-400">Validation Acc: 99.72%</span>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-gray-500 block text-[11px] uppercase tracking-wider">Held-Out Test Acc</span>
                  <span className="text-xl font-bold text-gray-900 mt-1 block">79.56%</span>
                  <span className="text-[10px] text-gray-400">Test Macro-F1: 79.54%</span>
                </div>
              </div>

              <div className="text-xs space-y-2 pt-2 border-t border-gray-100">
                <div className="flex justify-between text-gray-500">
                  <span>Macro Precision (Test):</span>
                  <span className="font-mono text-gray-800">82.38%</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>Macro Recall (Test):</span>
                  <span className="font-mono text-gray-800">81.60%</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>Weighted F1-Score (Test):</span>
                  <span className="font-mono text-gray-800">79.44%</span>
                </div>
              </div>
            </div>

            {/* Five-Class Model Card */}
            <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center border-b border-gray-100 pb-3">
                <span className="font-bold text-gray-900 text-base">Five-Class Detection</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-200 font-semibold">
                  Winner: Decision Tree
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-[#EDE9FE] rounded-lg border border-purple-200">
                  <span className="text-gray-500 block text-[11px] uppercase tracking-wider">Validation Macro-F1</span>
                  <span className="text-xl font-bold text-sky-600 mt-1 block">87.35%</span>
                  <span className="text-[10px] text-gray-400">Validation Acc: 99.68%</span>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-gray-500 block text-[11px] uppercase tracking-wider">Held-Out Test Acc</span>
                  <span className="text-xl font-bold text-gray-900 mt-1 block">74.05%</span>
                  <span className="text-[10px] text-gray-400">Test Macro-F1: 54.19%</span>
                </div>
              </div>

              <div className="text-xs space-y-2 pt-2 border-t border-gray-100">
                <div className="flex justify-between text-gray-500">
                  <span>Macro Precision (Test):</span>
                  <span className="font-mono text-gray-800">79.95%</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>Weighted F1-Score (Test):</span>
                  <span className="font-mono text-gray-800">70.46%</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>Zero-Day Test Generalization:</span>
                  <span className="font-mono text-amber-700 font-semibold">High DoS/Probe, Low R2L/U2R Recall</span>
                </div>
              </div>
            </div>
          </div>

          {/* Per-Class Metrics Table on Held-Out Test Set */}
          <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-5">
            <h3 className="font-bold text-gray-900 text-sm mb-1">
              Held-Out Test Set Per-Class Metrics (Five-Class Detection)
            </h3>
            <p className="text-xs text-gray-500 mb-3">
              Ground-truth performance on the 22,544 official test records:
            </p>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-400 uppercase tracking-wider bg-gray-50">
                    <th className="py-2.5 px-3">Class</th>
                    <th className="py-2.5 px-3">Precision</th>
                    <th className="py-2.5 px-3">Recall</th>
                    <th className="py-2.5 px-3">F1-Score</th>
                    <th className="py-2.5 px-3">Test Support (Records)</th>
                    <th className="py-2.5 px-3">Evaluation Insight</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-gray-700">
                  {(testMetrics?.five_class_test_per_class || []).map((row, idx) => {
                    const isLowRecall = row.recall < 0.25
                    return (
                      <tr key={idx} className={isLowRecall ? 'bg-amber-50/60' : 'hover:bg-gray-50'}>
                        <td className="py-2.5 px-3 font-semibold">
                          <span className={`px-2 py-0.5 rounded border text-[11px] ${getBadgeClass(row.class)}`}>
                            {row.class}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono">{(row.precision * 100).toFixed(2)}%</td>
                        <td className={`py-2.5 px-3 font-mono ${isLowRecall ? 'text-amber-700 font-bold' : ''}`}>
                          {(row.recall * 100).toFixed(2)}%
                        </td>
                        <td className="py-2.5 px-3 font-mono">{(row.f1 * 100).toFixed(2)}%</td>
                        <td className="py-2.5 px-3 font-mono">{row.support.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-[11px] text-gray-500">
                          {row.class === 'Normal' && 'High recall: very low false alarms on clean traffic'}
                          {row.class === 'DoS' && 'Strong detection on flooding patterns & SYN errors'}
                          {row.class === 'Probe' && 'Effective detection of port scanners and sweeps'}
                          {row.class === 'R2L' && 'Low recall due to 14 unseen password/exploit variants in test set'}
                          {row.class === 'U2R' && 'Small sample size (67 test records); unseen privilege exploits'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model Comparison Table */}
          <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-5">
            <h3 className="font-bold text-gray-900 text-sm mb-1">
              Algorithm Comparison on 80/20 Validation Split
            </h3>
            <p className="text-xs text-gray-500 mb-3">
              Logistic Regression vs Decision Tree vs Random Forest:
            </p>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-400 uppercase tracking-wider bg-gray-50">
                    <th className="py-2.5 px-3">Task</th>
                    <th className="py-2.5 px-3">Algorithm</th>
                    <th className="py-2.5 px-3">Accuracy</th>
                    <th className="py-2.5 px-3">Macro Precision</th>
                    <th className="py-2.5 px-3">Macro Recall</th>
                    <th className="py-2.5 px-3">Validation Macro-F1</th>
                    <th className="py-2.5 px-3">Weighted F1</th>
                    <th className="py-2.5 px-3">Train Time (s)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-gray-700 font-mono">
                  {(modelComparison?.binary_comparison || []).map((m, i) => (
                    <tr key={`bin_${i}`} className={m.model === 'Decision Tree' ? 'bg-emerald-50/50' : 'hover:bg-gray-50'}>
                      <td className="py-2 px-3 font-sans font-semibold text-gray-500">Binary</td>
                      <td className="py-2 px-3 font-sans font-bold text-gray-900 flex items-center space-x-1.5">
                        <span>{m.model}</span>
                        {m.model === 'Decision Tree' && (
                          <span className="text-[10px] text-emerald-700 font-sans px-1.5 rounded bg-emerald-100 border border-emerald-200">Selected</span>
                        )}
                      </td>
                      <td className="py-2 px-3">{(m.accuracy * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.macro_precision * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.macro_recall * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3 text-emerald-700 font-bold">{(m.macro_f1 * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.weighted_f1 * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{m.training_seconds}s</td>
                    </tr>
                  ))}
                  {(modelComparison?.five_class_comparison || []).map((m, i) => (
                    <tr key={`five_${i}`} className={m.model === 'Decision Tree' ? 'bg-sky-50/50' : 'hover:bg-gray-50'}>
                      <td className="py-2 px-3 font-sans font-semibold text-gray-500">Five-Class</td>
                      <td className="py-2 px-3 font-sans font-bold text-gray-900 flex items-center space-x-1.5">
                        <span>{m.model}</span>
                        {m.model === 'Decision Tree' && (
                          <span className="text-[10px] text-sky-700 font-sans px-1.5 rounded bg-sky-100 border border-sky-200">Selected</span>
                        )}
                      </td>
                      <td className="py-2 px-3">{(m.accuracy * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.macro_precision * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.macro_recall * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3 text-sky-700 font-bold">{(m.macro_f1 * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{(m.weighted_f1 * 100).toFixed(2)}%</td>
                      <td className="py-2 px-3">{m.training_seconds}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Test Confusion Matrices Gallery */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-4">
              <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">
                Binary Detection: Test Confusion Matrix
              </h4>
              <div className="bg-gray-50 border border-gray-100 p-2 rounded-lg flex justify-center">
                <img
                  src="/api/static/results/binary_detection_test_confusion_matrix.png"
                  alt="Binary Detection Test Confusion Matrix"
                  className="max-h-72 object-contain rounded"
                />
              </div>
            </div>

            <div className="bg-white border border-gray-200 shadow-sm rounded-xl p-4">
              <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">
                Five-Class Detection: Test Confusion Matrix
              </h4>
              <div className="bg-gray-50 border border-gray-100 p-2 rounded-lg flex justify-center">
                <img
                  src="/api/static/results/five_class_detection_test_confusion_matrix.png"
                  alt="Five-Class Detection Test Confusion Matrix"
                  className="max-h-72 object-contain rounded"
                />
              </div>
            </div>
          </div>

        </div>
      ) : (
        /* PREDICTION HISTORY AUDIT LOG TAB */
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-white border border-gray-200 shadow-sm rounded-xl p-4">
            <div className="flex items-center space-x-3">
              <Database className="w-5 h-5 text-[#6D28D9]" />
              <div>
                <span className="text-xs font-bold text-gray-800">Active Persistence Store:</span>
                <span className="text-xs text-gray-500 ml-2">
                  {historyData?.database_status === 'connected' ? (
                    <span className="text-emerald-700 font-semibold">MongoDB (intrusion_detection_db.prediction_history)</span>
                  ) : (
                    <span className="text-amber-700 font-semibold">Local Fallback File (prediction_history_fallback.json)</span>
                  )}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={fetchData}
                disabled={historyLoading}
                className="p-2 rounded-lg text-gray-400 hover:text-[#6D28D9] hover:bg-[#EDE9FE] text-xs flex items-center space-x-1 transition-colors"
                title="Refresh log"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={handleClearHistory}
                disabled={historyLoading || !historyData?.count}
                className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 text-xs font-medium flex items-center space-x-1.5 disabled:opacity-50 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear History</span>
              </button>
            </div>
          </div>

          <div className="bg-white border border-gray-200 shadow-sm rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-400 uppercase tracking-wider bg-gray-50">
                    <th className="py-3 px-4">Prediction ID</th>
                    <th className="py-3 px-4">Timestamp (UTC)</th>
                    <th className="py-3 px-4">Task</th>
                    <th className="py-3 px-4">Classification</th>
                    <th className="py-3 px-4">Confidence</th>
                    <th className="py-3 px-4">Inference Latency</th>
                    <th className="py-3 px-4">Storage Backend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-gray-700">
                  {(historyData?.history || []).length > 0 ? (
                    historyData.history.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="py-3 px-4 font-mono text-gray-400">{item.id}</td>
                        <td className="py-3 px-4 font-mono text-gray-400">
                          {new Date(item.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 font-semibold capitalize text-gray-700">
                          {item.task.replace('_', ' ')}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2.5 py-0.5 rounded-md font-bold border text-xs ${getBadgeClass(item.predicted_class)}`}>
                            {item.predicted_class}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono">
                          {(item.confidence * 100).toFixed(2)}%
                        </td>
                        <td className="py-3 px-4 font-mono text-gray-400">
                          {item.inference_time_ms} ms
                        </td>
                        <td className="py-3 px-4">
                          <span className={`text-[11px] font-semibold uppercase px-2 py-0.5 rounded border ${
                            item.storage_type === 'mongodb'
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : 'bg-amber-50 text-amber-700 border-amber-200'
                          }`}>
                            {item.storage_type || 'local_fallback'}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="py-12 text-center text-gray-400">
                        No predictions recorded yet. Run a classification in the Intrusion Detection tab!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
