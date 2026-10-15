import React from 'react'
import { Info, Database, CheckCircle2, AlertCircle } from 'lucide-react'

export default function HealthBanner({ health }) {
  const isMongo = health?.database?.status === 'connected'

  return (
    <div className="bg-[#F5F3FF] border-b border-[#EDE9FE] text-xs py-2 px-4 shadow-[inset_0_-1px_0_rgba(109,40,217,0.05)]">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-gray-600">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-[#6D28D9] shrink-0" />
          <span>
            <strong className="text-[#4C1D95]">Project Scope:</strong> Trained on NSL-KDD benchmark. Predictions execute through saved PySpark MLlib PipelineModels on connection feature vectors (no live interface packet sniffing).
          </span>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <Database className="w-3.5 h-3.5 text-gray-500" />
          <span>Persistence:</span>
          {isMongo ? (
            <span className="flex items-center text-emerald-700 font-medium space-x-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              <span>MongoDB Connected</span>
            </span>
          ) : (
            <span className="flex items-center text-amber-700 font-medium space-x-1" title={health?.database?.message}>
              <AlertCircle className="w-3 h-3 text-amber-600" />
              <span>Local Fallback Store ({health?.database?.total_records || 0} records)</span>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
