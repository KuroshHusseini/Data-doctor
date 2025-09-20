'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Download, FileText, Calendar, Clock, CheckCircle, AlertTriangle, Eye, RefreshCw } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface HistoryPanelProps {
  onClose: () => void
}

interface UploadHistory {
  _id: string
  upload_id: string
  filename: string
  file_size: number
  upload_time: string
  status: string
  quality_score?: number
  issues_count?: number
  has_cleaned_data?: boolean
  fixes_applied?: any[]
}

export default function HistoryPanel({ onClose }: HistoryPanelProps) {
  const [uploads, setUploads] = useState<UploadHistory[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/history')
      setUploads(response.data.uploads)
    } catch (error) {
      console.error('Error fetching history:', error)
      toast.error('Failed to load history')
    } finally {
      setIsLoading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'fixed':
        return <CheckCircle className="w-4 h-4 text-success-600" />
      case 'analyzed':
        return <AlertTriangle className="w-4 h-4 text-warning-600" />
      default:
        return <FileText className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fixed':
        return 'bg-success-100 text-success-800'
      case 'analyzed':
        return 'bg-warning-100 text-warning-800'
      case 'uploaded':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleDownload = async (uploadId: string, filename: string, type: 'cleaned' | 'original' = 'cleaned') => {
    try {
      const endpoint = type === 'cleaned' 
        ? `http://localhost:8000/download/${uploadId}`
        : `http://localhost:8000/download/original/${uploadId}`
      
      const response = await axios.get(endpoint, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', type === 'cleaned' ? `cleaned_${filename}` : filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success(`${type === 'cleaned' ? 'Cleaned' : 'Original'} file downloaded successfully!`)
    } catch (error: any) {
      console.error('Download error:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to download file'
      toast.error(errorMessage)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="relative w-full max-w-4xl h-[600px] glass-effect rounded-2xl shadow-soft-lg flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/20 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Upload History</h2>
            <p className="text-gray-600 dark:text-gray-300">View and download your previously processed datasets</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchHistory}
              className="p-2 hover:bg-white/20 dark:hover:bg-gray-800/20 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 dark:hover:bg-gray-800/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            </div>
          ) : uploads.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No uploads yet</h3>
              <p className="text-gray-600">Upload your first dataset to see it here</p>
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {uploads.map((upload, index) => (
                  <motion.div
                    key={upload._id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                    className="glass-effect p-6 hover:shadow-md transition-all duration-300 rounded-xl border border-white/20 dark:border-gray-700"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 dark:text-white truncate">{upload.filename}</h3>
                          <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-4 h-4" />
                              <span>{formatDate(upload.upload_time)}</span>
                            </div>
                            <span>{formatFileSize(upload.file_size)}</span>
                          </div>
                          
                          {/* Quality Score and Issues */}
                          {upload.quality_score !== undefined && (
                            <div className="flex items-center space-x-4 mt-2 text-sm">
                              <div className="flex items-center space-x-1">
                                <span className="text-gray-600 dark:text-gray-400">Quality:</span>
                                <span className={`font-medium ${upload.quality_score >= 80 ? 'text-green-600' : upload.quality_score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                                  {upload.quality_score}%
                                </span>
                              </div>
                              {upload.issues_count !== undefined && (
                                <div className="flex items-center space-x-1">
                                  <span className="text-gray-600 dark:text-gray-400">Issues:</span>
                                  <span className="font-medium">{upload.issues_count}</span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 ml-4">
                        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(upload.status)}`}>
                          {getStatusIcon(upload.status)}
                          <span className="capitalize">{upload.status}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {upload.has_cleaned_data && (
                            <button
                              onClick={() => handleDownload(upload.upload_id, upload.filename, 'cleaned')}
                              className="flex items-center space-x-1 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
                              title="Download cleaned data"
                            >
                              <Download className="w-4 h-4" />
                              <span>Cleaned</span>
                            </button>
                          )}
                          
                          <button
                            onClick={() => handleDownload(upload.upload_id, upload.filename, 'original')}
                            className="flex items-center space-x-1 px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
                            title="Download original file"
                          >
                            <Eye className="w-4 h-4" />
                            <span>Original</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/20 dark:border-gray-700 bg-white/10 dark:bg-gray-800/20 rounded-b-2xl">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>{uploads.length} total uploads</span>
            <span>Data is stored securely and can be accessed anytime</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
