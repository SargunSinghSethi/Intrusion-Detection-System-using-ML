"use client"

import { AlertTriangle, AlertCircle, Shield, CheckCircle2, Zap } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useState } from "react"

interface Threat {
  id: number
  type: string
  severity: "Low" | "Medium" | "High" | "Critical"
  description: string
  confidence: number
  sourceIP: string
  destinationIP: string
  port: number
}

interface AnalysisResultsProps {
  data: {
    job_id: number
    filename: string
    status: string
    threats: Threat[]
    summary: {
      totalThreats: number
      riskScore: number
      recommendation: string
    }
  }
}

const getSeverityColor = (severity: string) => {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    Critical: {
      bg: "bg-red-50",
      text: "text-red-900",
      border: "border-red-200",
    },
    High: {
      bg: "bg-orange-50",
      text: "text-orange-900",
      border: "border-orange-200",
    },
    Medium: {
      bg: "bg-yellow-50",
      text: "text-yellow-900",
      border: "border-yellow-200",
    },
    Low: {
      bg: "bg-blue-50",
      text: "text-blue-900",
      border: "border-blue-200",
    },
  }
  return colors[severity] || colors.Low
}

const getSeverityBadgeColor = (severity: string) => {
  const badges: Record<string, string> = {
    Critical: "bg-red-100 text-red-800",
    High: "bg-orange-100 text-orange-800",
    Medium: "bg-yellow-100 text-yellow-800",
    Low: "bg-blue-100 text-blue-800",
  }
  return badges[severity] || "bg-gray-100 text-gray-800"
}

const getRiskScoreColor = (score: number) => {
  if (score >= 80) return { bg: "bg-red-600", text: "text-white", label: "Critical" }
  if (score >= 60) return { bg: "bg-orange-600", text: "text-white", label: "High" }
  if (score >= 40) return { bg: "bg-yellow-600", text: "text-white", label: "Medium" }
  return { bg: "bg-green-600", text: "text-white", label: "Low" }
}

export function AnalysisResults({ data }: AnalysisResultsProps) {
  const [expandedThreat, setExpandedThreat] = useState<number | null>(null)
  const riskScoreColors = getRiskScoreColor(data.summary.riskScore) || "";

  return (
    <div className="w-full space-y-6">
      {/* Header with Risk Score */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Risk Score Card */}
        <Card className="p-6 flex flex-col items-center justify-center">
          <div className="relative w-32 h-32 mb-4">
            <div className={`absolute inset-0 rounded-full ${riskScoreColors.bg} opacity-20`}></div>
            <div
              className={`absolute inset-0 rounded-full ${riskScoreColors.bg} flex items-center justify-center`}
              style={{
                background: `conic-gradient(${riskScoreColors.bg} 0deg ${(data.summary.riskScore / 100) * 360}deg, #e5e7eb ${(data.summary.riskScore / 100) * 360}deg)`,
              }}
            >
              <div className="w-28 h-28 rounded-full bg-background flex items-center justify-center">
                <div className="text-center">
                  <div
                    className={`text-3xl font-bold ${riskScoreColors.text} ${riskScoreColors.bg} rounded-lg px-3 py-1`}
                  >
                    {data.summary.riskScore}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">Risk Score</p>
                </div>
              </div>
            </div>
          </div>
          <Badge className={`${getSeverityBadgeColor(riskScoreColors.label)}`}>{riskScoreColors.label}</Badge>
        </Card>

        {/* Summary Stats */}
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-orange-600 mt-1 flex-shrink-0" />
              <div>
                <p className="text-sm text-muted-foreground">Total Threats Detected</p>
                <p className="text-2xl font-bold text-foreground">{data.summary.totalThreats}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Shield className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
              <div>
                <p className="text-sm text-muted-foreground">Analysis Status</p>
                <p className="text-lg font-semibold text-green-700">Completed</p>
              </div>
            </div>
          </div>
        </Card>

        {/* File Info */}
        <Card className="p-6">
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Analyzed File</p>
              <p className="text-sm font-mono text-foreground truncate">{data.filename}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Job ID</p>
              <p className="text-sm font-mono text-foreground">{data.job_id}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Threats List */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Zap className="h-5 w-5 mr-2 text-orange-600" />
          Detected Threats ({data.threats.length})
        </h3>
        <div className="space-y-3">
          {data.threats.map((threat) => {
            const colors = getSeverityColor(threat.severity)
            const isExpanded = expandedThreat === threat.id

            return (
              <Card
                key={threat.id}
                className={`p-4 cursor-pointer transition-all ${colors.bg} border ${colors.border}`}
                onClick={() => setExpandedThreat(isExpanded ? null : threat.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <AlertCircle className={`h-5 w-5 ${colors.text}`} />
                      <h4 className={`font-semibold ${colors.text}`}>{threat.type}</h4>
                      <Badge className={getSeverityBadgeColor(threat.severity)}>{threat.severity}</Badge>
                      <Badge variant="outline" className="ml-auto">
                        {Math.round(threat.confidence * 100)}% Confidence
                      </Badge>
                    </div>
                    {isExpanded && (
                      <div className="mt-4 space-y-3 text-sm">
                        <p className={`${colors.text} leading-relaxed`}>{threat.description}</p>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-white bg-opacity-50 p-2 rounded">
                            <p className="text-xs text-muted-foreground">Source IP</p>
                            <p className="font-mono text-foreground">{threat.sourceIP}</p>
                          </div>
                          <div className="bg-white bg-opacity-50 p-2 rounded">
                            <p className="text-xs text-muted-foreground">Destination IP</p>
                            <p className="font-mono text-foreground">{threat.destinationIP}</p>
                          </div>
                          <div className="bg-white bg-opacity-50 p-2 rounded">
                            <p className="text-xs text-muted-foreground">Port</p>
                            <p className="font-mono text-foreground">{threat.port}</p>
                          </div>
                          <div className="bg-white bg-opacity-50 p-2 rounded">
                            <p className="text-xs text-muted-foreground">Threat ID</p>
                            <p className="font-mono text-foreground">#{threat.id}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Recommendations */}
      <Alert className="border-blue-200 bg-blue-50">
        <CheckCircle2 className="h-4 w-4 text-blue-600" />
        <AlertDescription className="ml-4 text-blue-900 text-sm leading-relaxed">
          <span className="font-semibold">Recommendations:</span>
          <div className="mt-2 space-y-2">
            {data.summary.recommendation
              .split("\n")
              .filter((line) => line.trim())
              .map((line, idx) => (
                <p key={idx} className="text-xs">
                  {line}
                </p>
              ))}
          </div>
        </AlertDescription>
      </Alert>
    </div>
  )
}
