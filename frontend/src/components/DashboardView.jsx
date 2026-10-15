import React from 'react'
import {
  ShieldAlert,
  Server,
  Layers,
  ArrowRight,
  TrendingUp,
  Cpu,
  FileSpreadsheet,
  Award
} from 'lucide-react'

export default function DashboardView({ setActiveTab }) {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-[#EDE9FE]/50 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#EDE9FE] border border-[#DDD6FE] text-[#6D28D9] text-xs font-semibold mb-4">
            <Cpu className="w-3.5 h-3.5 text-[#6D28D9]" />
            <span>Apache Spark & MLlib Distributed Processing Engine</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight leading-tight">
            Network Intrusion Detection & Big Data Analytics
          </h1>
          <p className="mt-3 text-gray-600 text-base leading-relaxed">
            A distributed big-data security platform leveraging Apache Spark, Scala RDDs, and PySpark MLlib pipelines on the benchmark NSL-KDD dataset to classify network attacks into binary and 5-class categories.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => setActiveTab('detection')}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-[#6D28D9] hover:bg-[#5B21B6] text-white font-medium text-sm transition-all shadow-sm shadow-purple-900/20"
            >
              <span>Test Intrusion Detection</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setActiveTab('evaluation')}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium text-sm transition-colors shadow-sm"
            >
              <span>View Review 3 Metrics</span>
            </button>
          </div>
        </div>
      </div>

      {/* Ground Truth Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Binary Validation F1</span>
            <div className="p-2 bg-[#EDE9FE] rounded-lg">
              <TrendingUp className="w-4 h-4 text-[#6D28D9]" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">99.72%</span>
            <span className="text-xs text-[#6D28D9] font-semibold bg-[#EDE9FE] px-2 py-0.5 rounded">Decision Tree</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Validation Split (80/20) Macro-F1
          </p>
          <div className="mt-3 text-xs pt-2.5 border-t border-gray-100 text-gray-500 flex justify-between">
            <span>Official Test Acc:</span>
            <span className="text-gray-900 font-semibold">79.56%</span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Five-Class Validation F1</span>
            <div className="p-2 bg-[#EDE9FE] rounded-lg">
              <Layers className="w-4 h-4 text-[#6D28D9]" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">87.35%</span>
            <span className="text-xs text-[#6D28D9] font-semibold bg-[#EDE9FE] px-2 py-0.5 rounded">Macro-F1</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Weighted-F1: 99.68% (Validation)
          </p>
          <div className="mt-3 text-xs pt-2.5 border-t border-gray-100 text-gray-500 flex justify-between">
            <span>Official Test Acc:</span>
            <span className="text-gray-900 font-semibold">74.05%</span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Dataset Volume</span>
            <div className="p-2 bg-[#EDE9FE] rounded-lg">
              <FileSpreadsheet className="w-4 h-4 text-[#6D28D9]" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">148,517</span>
            <span className="text-xs text-[#6D28D9] font-semibold bg-[#EDE9FE] px-2 py-0.5 rounded">Records</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Train: 125,973 • Held-Out Test: 22,544
          </p>
          <div className="mt-3 text-xs pt-2.5 border-t border-gray-100 text-gray-500 flex justify-between">
            <span>Features Processed:</span>
            <span className="text-gray-900 font-semibold">41 Attributes</span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] hover:shadow-md transition-all">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Algorithms Evaluated</span>
            <div className="p-2 bg-[#EDE9FE] rounded-lg">
              <Award className="w-4 h-4 text-[#6D28D9]" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-gray-900">3 Models</span>
            <span className="text-xs text-[#6D28D9] font-semibold bg-[#EDE9FE] px-2 py-0.5 rounded">Compared</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Logistic Regression, Decision Tree, Random Forest
          </p>
          <div className="mt-3 text-xs pt-2.5 border-t border-gray-100 text-gray-500 flex justify-between">
            <span>Selected Pipeline:</span>
            <span className="text-[#6D28D9] font-semibold">Decision Tree</span>
          </div>
        </div>
      </div>

      {/* Architecture Stages */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <Server className="w-5 h-5 text-[#6D28D9]" />
          <span>Distributed Architecture & Pipeline Workflow</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] transition-colors relative">
            <div className="text-xs font-bold text-[#6D28D9] uppercase tracking-wider mb-2">Stage 1</div>
            <h3 className="font-semibold text-gray-900 text-base mb-1">Preprocessing & Taxonomy</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Standardized 41 NSL-KDD features, filtered corrupted rows, and mapped 38 distinct attack labels into 4 standard threat categories (DoS, Probe, R2L, U2R) + Normal.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] transition-colors relative">
            <div className="text-xs font-bold text-[#6D28D9] uppercase tracking-wider mb-2">Stage 2</div>
            <h3 className="font-semibold text-gray-900 text-base mb-1">Spark RDD Analytics</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Distributed MapReduce & Scala RDD analysis with custom partitioners, computing protocol distributions, service error rates, and connection frequency profiles.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] transition-colors relative">
            <div className="text-xs font-bold text-[#6D28D9] uppercase tracking-wider mb-2">Stage 3</div>
            <h3 className="font-semibold text-gray-900 text-base mb-1">PySpark MLlib Pipelines</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              7-stage MLlib Pipeline combining StringIndexer, OneHotEncoder, VectorAssembler (124 feature dimensions), and Decision Tree Classifier trained on 8 partitions.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:border-[#DDD6FE] transition-colors relative">
            <div className="text-xs font-bold text-[#6D28D9] uppercase tracking-wider mb-2">Stage 4</div>
            <h3 className="font-semibold text-gray-900 text-base mb-1">FastAPI & MongoDB Storage</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Low-latency FastAPI REST service serving saved models with live inference, probability distributions, and persistent MongoDB history (with offline fallback store).
            </p>
          </div>
        </div>
      </div>

      {/* Attack Taxonomy Table */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-[#6D28D9]" />
          <span>NSL-KDD Attack Category Mapping</span>
        </h2>
        <p className="text-xs text-gray-500 mb-4">
          Hierarchical five-class categorization implemented across the Big Data pipeline:
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-xs">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50/80 text-gray-600 uppercase tracking-wider">
                <th className="py-3 px-3.5 font-semibold">Category</th>
                <th className="py-3 px-3.5 font-semibold">Class Description</th>
                <th className="py-3 px-3.5 font-semibold">Representative Attack Signatures</th>
                <th className="py-3 px-3.5 font-semibold">Key Discriminative Features</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              <tr className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 px-3.5 font-bold text-emerald-700">Normal</td>
                <td className="py-3 px-3.5">Legitimate user traffic</td>
                <td className="py-3 px-3.5 font-mono text-gray-600 bg-gray-50 px-2 rounded">normal</td>
                <td className="py-3 px-3.5">SF flag, balanced src/dst bytes, zero error rates</td>
              </tr>
              <tr className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 px-3.5 font-bold text-rose-700">DoS (Denial of Service)</td>
                <td className="py-3 px-3.5">Exhausts computing or memory bandwidth</td>
                <td className="py-3 px-3.5 font-mono text-gray-600 bg-gray-50 px-2 rounded">neptune, smurf, back, teardrop, pod, apache2</td>
                <td className="py-3 px-3.5">High count, serror_rate=1.0, S0 connection flag</td>
              </tr>
              <tr className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 px-3.5 font-bold text-amber-700">Probe (Surveillance)</td>
                <td className="py-3 px-3.5">Scans networks to map vulnerabilities</td>
                <td className="py-3 px-3.5 font-mono text-gray-600 bg-gray-50 px-2 rounded">satan, ipsweep, portsweep, nmap, mscan</td>
                <td className="py-3 px-3.5">High diff_srv_rate, REJ flags, rerror_rate</td>
              </tr>
              <tr className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 px-3.5 font-bold text-[#6D28D9]">R2L (Remote to Local)</td>
                <td className="py-3 px-3.5">Unauthorized access from remote machine</td>
                <td className="py-3 px-3.5 font-mono text-gray-600 bg-gray-50 px-2 rounded">guess_passwd, ftp_write, imap, phf, warezclient</td>
                <td className="py-3 px-3.5">num_failed_logins &gt; 0, hot indicators, is_guest_login</td>
              </tr>
              <tr className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 px-3.5 font-bold text-indigo-700">U2R (User to Root)</td>
                <td className="py-3 px-3.5">Privilege escalation to root privileges</td>
                <td className="py-3 px-3.5 font-mono text-gray-600 bg-gray-50 px-2 rounded">buffer_overflow, loadmodule, perl, rootkit</td>
                <td className="py-3 px-3.5">root_shell=1, num_root, num_file_creations</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
