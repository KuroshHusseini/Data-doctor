'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Download, CheckCircle, FileText, AlertCircle, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

interface DownloadPanelProps {
  uploadData: any
  analysisData: any
  fixData: any
  onClose: () => void
}

export default function DownloadPanel({ uploadData, analysisData, fixData, onClose }: DownloadPanelProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [downloadComplete, setDownloadComplete] = useState(false)

  const handleDownload = async (type: 'cleaned' | 'original' = 'cleaned') => {
    if (!uploadData?.upload_id) return

    setIsDownloading(true)
    setDownloadProgress(0)

    try {
      const endpoint = type === 'cleaned' 
        ? `http://localhost:8000/download/${uploadData.upload_id}`
        : `http://localhost:8000/download/original/${uploadData.upload_id}`
      
      // Simulate download progress
      const progressInterval = setInterval(() => {
        setDownloadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + Math.random() * 20
        })
      }, 200)

      const response = await axios.get(endpoint, {
        responseType: 'blob'
      })
      
      // Complete progress
      setDownloadProgress(100)
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', type === 'cleaned' 
        ? `cleaned_${uploadData.filename || 'data.csv'}` 
        : uploadData.filename || 'original_data.csv'
      )
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      setDownloadComplete(true)
      toast.success(`${type === 'cleaned' ? 'Cleaned' : 'Original'} file downloaded successfully!`)
      
      setTimeout(() => {
        setDownloadComplete(false)
        setDownloadProgress(0)
      }, 2000)
      
    } catch (error: any) {
      console.error('Download error:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to download file'
      toast.error(errorMessage)
    } finally {
      setIsDownloading(false)
    }
  }

  const getFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="w-full max-w-2xl glass-effect rounded-2xl shadow-soft-lg"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/20 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-700 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Data Cleanup Complete!</h2>
              <p className="text-gray-600 dark:text-gray-300">Your dataset has been processed and is ready for download</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 dark:hover:bg-gray-800/20 rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Summary */}
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h3 className="font-semibold text-green-800 dark:text-green-200">Cleanup Summary</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-green-700 dark:text-green-300">Original rows:</span>
                <span className="font-medium ml-2">{fixData?.before_after_comparison?.original_rows || 'N/A'}</span>
              </div>
              <div>
                <span className="text-green-700 dark:text-green-300">Cleaned rows:</span>
                <span className="font-medium ml-2">{fixData?.before_after_comparison?.cleaned_rows || 'N/A'}</span>
              </div>
              <div>
                <span className="text-green-700 dark:text-green-300">Duplicates removed:</span>
                <span className="font-medium ml-2">{fixData?.before_after_comparison?.duplicates_removed || 0}</span>
              </div>
              <div>
                <span className="text-green-700 dark:text-green-300">Missing values filled:</span>
                <span className="font-medium ml-2">{fixData?.before_after_comparison?.missing_values_filled || 0}</span>
              </div>
            </div>
          </div>

          {/* Download Options */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Download Options</h3>
            
            {/* Cleaned Data */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Cleaned Dataset</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {getFileSize(uploadData?.file_size || 0)} • Ready for analysis
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDownload('cleaned')}
                  disabled={isDownloading}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isDownloading && downloadProgress > 0 ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>{Math.round(downloadProgress)}%</span>
                    </>
                  ) : downloadComplete ? (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      <span>Downloaded</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </>
                  )}
                </button>
              </div>
              
              {/* Progress Bar */}
              {isDownloading && downloadProgress > 0 && (
                <div className="mt-3">
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${downloadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Original Data */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Original Dataset</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {getFileSize(uploadData?.file_size || 0)} • Before cleanup
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDownload('original')}
                  disabled={isDownloading}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          </div>

          {/* Chat Suggestion */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 className="font-semibold text-blue-800 dark:text-blue-200">AI Chat Available</h3>
            </div>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              The chat panel has opened automatically. You can now ask questions about your cleaned data, 
              such as "What issues were fixed?" or "How can I use this data for analysis?"
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/20 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Your data is processed and ready for use
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
