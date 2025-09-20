'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, Info, TrendingUp, FileText, Zap } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface DataAnalysisProps {
  uploadData: any
  onComplete: (data: any) => void
}

export default function DataAnalysis({ uploadData, onComplete }: DataAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisData, setAnalysisData] = useState<any>(null)

  useEffect(() => {
    if (uploadData?.upload_id) {
      analyzeData()
    }
  }, [uploadData])

  const analyzeData = async () => {
    setIsAnalyzing(true)
    try {
      const response = await axios.post(`http://localhost:8000/analyze/${uploadData.upload_id}`)
      setAnalysisData(response.data)
      toast.success('Data analysis completed!')
      onComplete(response.data)
    } catch (error) {
      console.error('Analysis error:', error)
      toast.error('Failed to analyze data. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-error-600 bg-error-100'
      case 'high': return 'text-error-600 bg-error-100'
      case 'medium': return 'text-warning-600 bg-warning-100'
      case 'low': return 'text-blue-600 bg-blue-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getIssueIcon = (issueType: string) => {
    switch (issueType) {
      case 'missing_values': return <AlertTriangle className="w-4 h-4" />
      case 'duplicates': return <FileText className="w-4 h-4" />
      case 'format_errors': return <AlertTriangle className="w-4 h-4" />
      case 'outliers': return <TrendingUp className="w-4 h-4" />
      default: return <Info className="w-4 h-4" />
    }
  }

  if (isAnalyzing) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
        <h2 className="text-2xl font-bold mb-2">Analyzing Your Data</h2>
        <p className="text-gray-600">
          Our AI is examining your dataset for quality issues...
        </p>
      </div>
    )
  }

  if (!analysisData) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to Analyze</h2>
        <p className="text-gray-600 mb-6">
          Click the button below to start analyzing your uploaded data.
        </p>
        <button 
          onClick={analyzeData}
          className="btn-primary"
        >
          Start Analysis
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Data Quality Analysis</h2>
        <p className="text-gray-600">
          Here's what we found in your dataset
        </p>
      </div>

      {/* Quality Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Overall Quality Score</h3>
          <div className="flex items-center space-x-2">
            <div className="w-24 h-3 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className={`h-full ${analysisData.quality_score >= 0.8 ? 'bg-success-500' : 
                  analysisData.quality_score >= 0.6 ? 'bg-warning-500' : 'bg-error-500'}`}
                initial={{ width: 0 }}
                animate={{ width: `${analysisData.quality_score * 100}%` }}
                transition={{ duration: 1, delay: 0.5 }}
              />
            </div>
            <span className="text-lg font-bold">
              {Math.round(analysisData.quality_score * 100)}%
            </span>
          </div>
        </div>
        <p className="text-gray-600">
          {analysisData.quality_score >= 0.8 ? 'Excellent data quality!' :
           analysisData.quality_score >= 0.6 ? 'Good data quality with some issues to address.' :
           'Data quality needs improvement. Several issues detected.'}
        </p>
      </motion.div>

      {/* Issues Found */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Issues Detected</h3>
        {analysisData.issues_found.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-16 h-16 mx-auto text-success-600 mb-4" />
            <p className="text-lg font-medium text-gray-900">No issues found!</p>
            <p className="text-gray-600">Your data looks clean and ready to use.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {analysisData.issues_found.map((issue: any, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg"
              >
                <div className={`p-2 rounded-lg ${getSeverityColor(issue.severity)}`}>
                  {getIssueIcon(issue.issue_type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium text-gray-900 capitalize">
                      {issue.issue_type.replace('_', ' ')}
                    </h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-2">{issue.description}</p>
                  {issue.suggested_fix && (
                    <p className="text-blue-600 text-sm">
                      <strong>Suggestion:</strong> {issue.suggested_fix}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Recommendations */}
      {analysisData.recommendations && analysisData.recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
          <div className="space-y-3">
            {analysisData.recommendations.map((recommendation: string, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-start space-x-3"
              >
                <Zap className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
                <p className="text-gray-700">{recommendation}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Next Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="text-center"
      >
        <button 
          onClick={() => onComplete(analysisData)}
          className="btn-primary"
        >
          Proceed to Fix Issues
        </button>
      </motion.div>
    </div>
  )
}
