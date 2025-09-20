'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, AlertTriangle, Info, CheckCircle, X, RefreshCw } from 'lucide-react'

interface ValidationError {
  type: string
  message: string
  details?: string
  suggestion: string
}

interface ValidationWarning {
  type: string
  message: string
  details?: string
  suggestion: string
}

interface ValidationErrorsProps {
  errors: ValidationError[]
  warnings: ValidationWarning[]
  onDismiss?: () => void
  onRetry?: () => void
}

export default function ValidationErrors({ 
  errors, 
  warnings, 
  onDismiss, 
  onRetry 
}: ValidationErrorsProps) {
  const getErrorIcon = (type: string) => {
    switch (type) {
      case 'file_too_large':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'unsupported_format':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'empty_file':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'csv_parse_error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'excel_read_error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'json_parse_error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-red-600" />
    }
  }

  const getWarningIcon = (type: string) => {
    switch (type) {
      case 'missing_headers':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'insufficient_data':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'missing_required_headers':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'duplicate_headers':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
    }
  }

  const getErrorTitle = (type: string) => {
    switch (type) {
      case 'file_too_large':
        return 'File Too Large'
      case 'unsupported_format':
        return 'Unsupported File Format'
      case 'empty_file':
        return 'Empty File'
      case 'csv_parse_error':
        return 'CSV Format Error'
      case 'excel_read_error':
        return 'Excel Format Error'
      case 'json_parse_error':
        return 'JSON Format Error'
      default:
        return 'Validation Error'
    }
  }

  const getWarningTitle = (type: string) => {
    switch (type) {
      case 'missing_headers':
        return 'Missing Headers'
      case 'insufficient_data':
        return 'Limited Data'
      case 'missing_required_headers':
        return 'Recommended Headers Missing'
      case 'duplicate_headers':
        return 'Duplicate Headers'
      default:
        return 'Warning'
    }
  }

  if (errors.length === 0 && warnings.length === 0) {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-4"
    >
      {/* Errors */}
      {errors.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span>Upload Failed ({errors.length} error{errors.length > 1 ? 's' : ''})</span>
          </h3>
          
          {errors.map((error, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {getErrorIcon(error.type)}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-red-800 dark:text-red-200">
                    {getErrorTitle(error.type)}
                  </h4>
                  <p className="text-red-700 dark:text-red-300 mt-1">
                    {error.message}
                  </p>
                  {error.details && (
                    <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                      {error.details}
                    </p>
                  )}
                  <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/30 rounded border-l-4 border-red-500">
                    <p className="text-sm text-red-800 dark:text-red-200 font-medium">
                      💡 {error.suggestion}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5" />
            <span>Warnings ({warnings.length})</span>
          </h3>
          
          {warnings.map((warning, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (errors.length + index) * 0.1 }}
              className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {getWarningIcon(warning.type)}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-yellow-800 dark:text-yellow-200">
                    {getWarningTitle(warning.type)}
                  </h4>
                  <p className="text-yellow-700 dark:text-yellow-300 mt-1">
                    {warning.message}
                  </p>
                  {warning.details && (
                    <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
                      {warning.details}
                    </p>
                  )}
                  <div className="mt-2 p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded border-l-4 border-yellow-500">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
                      💡 {warning.suggestion}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {errors.length > 0 ? (
            <span>Please fix the errors above before uploading</span>
          ) : (
            <span>You can proceed with upload, but consider addressing the warnings</span>
          )}
        </div>
        
        <div className="flex items-center space-x-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Try Again</span>
            </button>
          )}
          
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              <X className="w-4 h-4" />
              <span>Dismiss</span>
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}
