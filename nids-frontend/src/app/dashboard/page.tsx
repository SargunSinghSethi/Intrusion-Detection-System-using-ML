"use client"

import { useUser, UserButton, useAuth } from "@clerk/nextjs"
import { Shield, Upload, ArrowRight, History, FileText, AlertCircle } from "lucide-react"
import { motion } from "framer-motion"
import { useState, useRef } from "react"
import Link from "next/link"
import { AnalysisResults } from "@/components/analysis-results"

export default function DashboardPage() {
  const { user, isLoaded } = useUser()
  const { getToken } = useAuth()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [jobId, setJobId] = useState<number | null>(null)
  const [status, setStatus] = useState<string>("")
  const [analysisResult, setAnalysisResultState] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const pollJobStatus = (jobId: number) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/upload?jobId=${jobId}`)
        if (!response.ok) throw new Error("Status check failed")
        const data = await response.json()

        setStatus(data.status)

        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval)
          setIsProcessing(false)

          if (data.status === "completed") {
            fetchResult(jobId)
          } else {
            setAnalysisResultState({
              status: "Failed",
              error: "Analysis failed. Please try again.",
              timestamp: new Date().toISOString(),
            })
          }
        }
      } catch (err) {
        console.error("Polling failed:", err)
        clearInterval(interval)
        setIsProcessing(false)
      }
    }, 5000)
  }

  const fetchResult = async (jobId: number) => {
    try {
      const response = await fetch(`/api/result/${jobId}`)
      if (!response.ok) throw new Error("Result fetch failed")
      const data = await response.json()
      setAnalysisResultState(data)
    } catch (err) {
      console.error("Result fetch failed:", err)
      setAnalysisResultState({
        status: "Failed",
        error: "Failed to fetch analysis result",
        timestamp: new Date().toISOString(),
      })
    }
  }

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">NIDS Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/history">
                <button className="btn-secondary flex items-center space-x-2">
                  <History className="h-4 w-4" />
                  <span>View History</span>
                </button>
              </Link>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back, {user?.firstName || "User"}!</h1>
          <p className="text-gray-600">
            Upload network logs or packet captures for real-time intrusion detection analysis.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* File Upload Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="card"
          >
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Upload className="h-6 w-6 mr-2 text-primary-600" />
              Upload Network Data
            </h2>

            <div className="space-y-6">
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) {
                      setSelectedFile(file)
                      setAnalysisResultState(null)
                      setStatus("")
                    }
                  }}
                  accept=".pcap,.log,.txt,.csv"
                  className="hidden"
                />
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {selectedFile ? selectedFile.name : "Click to upload file"}
                </p>
                <p className="text-gray-500">Supports .pcap, .log, .txt, .csv files</p>
                {selectedFile && (
                  <p className="text-sm text-gray-400 mt-2">Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                )}
              </div>

              <button
                onClick={() => {
                  if (!selectedFile) return
                  setIsProcessing(true)
                  setAnalysisResultState(null)
                  setStatus("Uploading in chunks...")

                  const chunkSize = 100 * 1024 * 1024
                  const totalChunks = Math.ceil(selectedFile.size / chunkSize)
                  const uploadId = crypto.randomUUID()

                  getToken().then((token) => {
                    let uploadedChunks = 0
                    const uploadChunk = async (i: number) => {
                      const chunk = selectedFile.slice(i * chunkSize, (i + 1) * chunkSize)
                      const formData = new FormData()
                      formData.append("chunk", chunk)
                      formData.append("filename", selectedFile.name)
                      formData.append("chunkIndex", i.toString())
                      formData.append("totalChunks", totalChunks.toString())
                      formData.append("uploadId", uploadId)

                      try {
                        const res = await fetch("/api/upload-chunk", { method: "POST", body: formData })
                        if (!res.ok) throw new Error(`Chunk ${i} failed`)
                        uploadedChunks++
                        setStatus(`Uploading... ${uploadedChunks}/${totalChunks}`)

                        if (uploadedChunks === totalChunks) {
                          const mergeRes = await fetch("/api/merge-chunks", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ filename: selectedFile.name, uploadId }),
                          })

                          if (!mergeRes.ok) throw new Error("Failed to merge chunks")

                          const data = await mergeRes.json()
                          setJobId(data.job_id)
                          setStatus("Processing started...")
                          pollJobStatus(data.job_id)
                        }
                      } catch (err) {
                        console.error(err)
                        setStatus("Upload failed. Please try again.")
                        setIsProcessing(false)
                      }
                    }

                    for (let i = 0; i < totalChunks; i++) {
                      uploadChunk(i)
                    }
                  })
                }}
                disabled={!selectedFile || isProcessing}
                className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>{status || "Analyzing..."}</span>
                  </>
                ) : (
                  <>
                    <span>Analyze File</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>

              {status && !isProcessing && <p className="text-center text-sm text-gray-500 mt-2">{status}</p>}
            </div>
          </motion.div>

          {/* Analysis Results Section - Always visible alongside upload section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="card"
          >
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <AlertCircle className="h-6 w-6 mr-2 text-primary-600" />
              Analysis Results
            </h2>

            {!analysisResult && !isProcessing && (
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg">Upload a file to see analysis results</p>
              </div>
            )}

            {isProcessing && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-lg text-gray-600">Analyzing your file...</p>
                <p className="text-sm text-gray-500 mt-2">{status || "This may take a few moments"}</p>
              </div>
            )}

            {analysisResult && <AnalysisResults data={analysisResult} />}
          </motion.div>
        </div>

        {/* Analyze Another File Button - Only show when results are displayed */}
        {analysisResult && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            onClick={() => {
              setAnalysisResultState(null)
              setSelectedFile(null)
              setStatus("")
              setJobId(null)
            }}
            className="mt-6 w-full btn-secondary"
          >
            Analyze Another File
          </motion.button>
        )}
      </div>
    </div>
  )
}
