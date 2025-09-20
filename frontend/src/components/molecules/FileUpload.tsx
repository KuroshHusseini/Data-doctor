'use client'

import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileText, AlertCircle, CheckCircle, X, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import FileSizeHelper from './FileSizeHelper'

interface FileUploadProps {
  onComplete: (data: any) => void
}

export default function FileUpload({ onComplete }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadId, setUploadId] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'completed' | 'error' | 'cancelled'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [showSizeHelper, setShowSizeHelper] = useState(false)
  const [rejectedFile, setRejectedFile] = useState<File | null>(null)

  // Poll upload status
  useEffect(() => {
    if (!uploadId || uploadStatus === 'completed' || uploadStatus === 'error' || uploadStatus === 'cancelled') {
      return
    }

    const pollStatus = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/upload/${uploadId}/status`)
        const status = response.data
        
        setUploadProgress(status.progress)
        setUploadStatus(status.status)
        
        if (status.status === 'uploaded') {
          setUploadStatus('completed')
          setIsUploading(false)
          toast.success('File uploaded successfully!')
          onComplete({
            upload_id: uploadId,
            filename: status.filename,
            file_size: status.file_size,
            upload_time: new Date(),
            status: 'uploaded'
          })
        } else if (status.status === 'error') {
          setUploadStatus('error')
          setError(status.error || 'Upload failed')
          setIsUploading(false)
          toast.error(status.error || 'Upload failed')
        }
      } catch (error) {
        console.error('Status polling error:', error)
        setUploadStatus('error')
        setError('Failed to check upload status')
        setIsUploading(false)
      }
    }

    const interval = setInterval(pollStatus, 1000) // Poll every second
    return () => clearInterval(interval)
  }, [uploadId, uploadStatus, onComplete])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Check file size (100MB limit)
    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2)
      const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(0)
      
      setUploadStatus('error')
      setError(`File too large: ${fileSizeMB}MB. Maximum size is ${maxSizeMB}MB.`)
      setRejectedFile(file)
      setShowSizeHelper(true)
      toast.error(`File too large: ${fileSizeMB}MB. Maximum size is ${maxSizeMB}MB.`)
      return
    }

    // If there's an existing upload, replace it
    if (uploadId && uploadStatus === 'uploading') {
      await cancelUpload()
    }

    setUploadedFile(file)
    setIsUploading(true)
    setUploadStatus('uploading')
    setUploadProgress(0)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadId(response.data.upload_id)
      toast.success('Upload started!')
    } catch (error: any) {
      console.error('Upload error:', error)
      setUploadStatus('error')
      setError(error.response?.data?.message || 'Failed to start upload')
      setIsUploading(false)
      toast.error(error.response?.data?.message || 'Failed to start upload')
    }
  }, [uploadId, uploadStatus])

  const cancelUpload = async () => {
    if (!uploadId) return

    try {
      await axios.delete(`http://localhost:8000/upload/${uploadId}`)
      setUploadStatus('cancelled')
      setIsUploading(false)
      setUploadProgress(0)
      toast.info('Upload cancelled')
    } catch (error) {
      console.error('Cancel upload error:', error)
      toast.error('Failed to cancel upload')
    }
  }

  const replaceUpload = async (file: File) => {
    if (!uploadId) return

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`http://localhost:8000/upload/${uploadId}/replace`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadId(response.data.upload_id)
      setUploadedFile(file)
      setUploadStatus('uploading')
      setUploadProgress(0)
      setError(null)
      toast.success('File replaced successfully!')
    } catch (error: any) {
      console.error('Replace upload error:', error)
      setError(error.response?.data?.message || 'Failed to replace file')
      toast.error(error.response?.data?.message || 'Failed to replace file')
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
    },
    multiple: false,
  })

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Upload Your Data</h2>
        <p className="text-gray-600">
          Drag and drop your file or click to browse. We support CSV, Excel, and JSON formats.
        </p>
      </div>

      <motion.div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />
        
        {uploadStatus === 'uploading' ? (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">Uploading...</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-1">{Math.round(uploadProgress)}%</p>
            </div>
            <button
              onClick={cancelUpload}
              className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors mx-auto"
            >
              <X className="w-4 h-4" />
              <span>Cancel Upload</span>
            </button>
          </div>
        ) : uploadStatus === 'completed' ? (
          <div className="space-y-4">
            <CheckCircle className="w-16 h-16 mx-auto text-success-600" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-900">{uploadedFile?.name}</p>
              <p className="text-sm text-gray-600">
                {(uploadedFile?.size! / 1024 / 1024).toFixed(2)} MB
              </p>
              <p className="text-sm text-success-600 mt-2">✓ Upload completed</p>
            </div>
            <button
              onClick={() => {
                setUploadedFile(null)
                setUploadId(null)
                setUploadStatus('idle')
                setUploadProgress(0)
                setError(null)
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors mx-auto"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Upload New File</span>
            </button>
          </div>
        ) : uploadStatus === 'error' ? (
          <div className="space-y-4">
            <AlertCircle className="w-16 h-16 mx-auto text-red-600" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-900">Upload Failed</p>
              <p className="text-sm text-red-600 mt-2">{error}</p>
            </div>
            <div className="flex space-x-3 justify-center">
              {error?.includes('too large') && (
                <button
                  onClick={() => setShowSizeHelper(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>Get Help</span>
                </button>
              )}
              <button
                onClick={() => {
                  setUploadedFile(null)
                  setUploadId(null)
                  setUploadStatus('idle')
                  setUploadProgress(0)
                  setError(null)
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Try Again</span>
              </button>
            </div>
          </div>
        ) : uploadStatus === 'cancelled' ? (
          <div className="space-y-4">
            <X className="w-16 h-16 mx-auto text-gray-400" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">Upload Cancelled</p>
              <p className="text-sm text-gray-500 mt-2">You can start a new upload</p>
            </div>
            <button
              onClick={() => {
                setUploadedFile(null)
                setUploadId(null)
                setUploadStatus('idle')
                setUploadProgress(0)
                setError(null)
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors mx-auto"
            >
              <Upload className="w-4 h-4" />
              <span>Start New Upload</span>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-16 h-16 mx-auto text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive ? 'Drop your file here' : 'Choose a file or drag it here'}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                CSV, Excel (.xlsx, .xls), or JSON files
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* File Requirements */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">File Requirements:</p>
            <ul className="space-y-1 text-blue-700">
              <li>• <strong>Maximum file size: 100MB</strong> (larger files will be rejected)</li>
              <li>• Supported formats: CSV, Excel (.xlsx, .xls), JSON</li>
              <li>• First row should contain column headers</li>
              <li>• UTF-8 encoding recommended</li>
            </ul>
            <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded-lg">
              <p className="text-xs text-yellow-800">
                <strong>Large files:</strong> Files over 50MB will use optimized chunked processing for better performance.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Supported Formats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { format: 'CSV', description: 'Comma-separated values', icon: '📊' },
          { format: 'Excel', description: 'Spreadsheet files', icon: '📈' },
          { format: 'JSON', description: 'JavaScript Object Notation', icon: '📋' }
        ].map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <span className="text-2xl">{item.icon}</span>
            <div>
              <p className="font-medium text-gray-900">{item.format}</p>
              <p className="text-sm text-gray-600">{item.description}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* File Size Helper Modal */}
      {showSizeHelper && rejectedFile && (
        <FileSizeHelper
          fileSize={rejectedFile.size}
          maxSize={100 * 1024 * 1024} // 100MB
          onClose={() => {
            setShowSizeHelper(false)
            setRejectedFile(null)
            setUploadStatus('idle')
            setError(null)
          }}
        />
      )}
    </div>
  )
}
