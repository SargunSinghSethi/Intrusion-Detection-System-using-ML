'use client'

import { useUser, UserButton } from '@clerk/nextjs'
import { Shield, ArrowLeft, Clock, AlertTriangle, CheckCircle, FileText, Eye } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { useEffect, useState } from 'react'

type HistoryItem = {
  pcap_id: number
  filename: string
  status: 'completed' | 'processing' | 'failed' | string
  threats_detected: number
  severity: 'High' | 'Medium' | 'Low' | string
  timestamp: string
}

export default function HistoryPage() {
  const { isLoaded } = useUser()
  const [analysisHistory, setAnalysisHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAnalysis, setSelectedAnalysis] = useState<number | null>(null)

  useEffect(() => {
    if (isLoaded) fetchHistory()
  }, [isLoaded])

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/history')
      if (!response.ok) throw new Error('Failed to fetch history')
      const data = await response.json()
      setAnalysisHistory(data)
    } catch (err: any) {
      console.error('Fetch error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'High': return 'text-red-600 bg-red-100'
      case 'Medium': return 'text-yellow-600 bg-yellow-100'
      case 'Low': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'processing': return <Clock className="h-4 w-4 text-blue-600" />
      case 'failed': return <AlertTriangle className="h-4 w-4 text-red-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  // Helper only if you still want “Malicious/Benign/Processing” style labels in stats
  const severityToLabel = (severity: string) => {
    if (severity === 'High') return 'malicious'
    if (severity === 'Low') return 'benign'
    return 'suspicious'
  }

  if (!isLoaded || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        Error: {error}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Dashboard</span>
              </Link>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-primary-600" />
                <span className="text-2xl font-bold text-gray-900">Analysis History</span>
              </div>
            </div>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis History</h1>
          <p className="text-gray-600">
            View all your previous network analysis results and threat detections.
          </p>
        </motion.div>

        {/* Stats Cards */}
        {analysisHistory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid md:grid-cols-4 gap-6 mb-8"
          >
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {analysisHistory.length}
              </div>
              <div className="text-gray-600">Total Analyses</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">
                {analysisHistory.filter(a => a.severity === 'High').length}
              </div>
              <div className="text-gray-600">Malicious Files</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {analysisHistory.filter(a => a.severity === 'Low').length}
              </div>
              <div className="text-gray-600">Benign Files</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">
                {analysisHistory.filter(a => a.status === 'processing').length}
              </div>
              <div className="text-gray-600">Processing</div>
            </div>
          </motion.div>
        )}

        {/* History List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="space-y-4"
        >
          {analysisHistory.map((item, index) => (
            <motion.div
              key={item.pcap_id || index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="card hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {item.filename}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(item.status)}
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {item.status}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {/* Use server severity directly */}
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(item.severity)}`}
                    >
                      {item.severity}
                    </span>
                  </div>

                  <button
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    onClick={() =>
                      setSelectedAnalysis(
                        selectedAnalysis === item.pcap_id ? null : item.pcap_id
                      )
                    }
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Expanded details */}
              {selectedAnalysis === item.pcap_id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 pt-4 border-t border-gray-200"
                >
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">
                        Analysis Details
                      </h4>
                      <div className="space-y-2 text-sm text-gray-600">
                        <div>Filename: {item.filename}</div>
                        <div>Status: {item.status}</div>
                        <div>Severity: {item.severity}</div>
                        <div>Threats Detected: {item.threats_detected}</div>
                        <div>Date: {new Date(item.timestamp).toLocaleString()}</div>
                        {/* If you still want a “Result” line */}
                        <div>Result: {severityToLabel(item.severity)}</div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Actions</h4>
                      <div className="flex space-x-2">
                        <button className="btn-primary text-sm px-3 py-1">
                          View Details
                        </button>
                        <button className="btn-secondary text-sm px-3 py-1">
                          Download Report
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {analysisHistory.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center py-12"
          >
            <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis History</h3>
            <p className="text-gray-600 mb-6">Upload your first file to start analyzing network data.</p>
            <Link href="/dashboard" className="btn-primary">
              Go to Dashboard
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  )
}
