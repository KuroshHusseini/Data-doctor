'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, X, RefreshCw, Info, ChevronDown, ChevronUp } from 'lucide-react'

interface ErrorDisplayProps {
  error: string | Error
  onRetry?: () => void
  onDismiss?: () => void
  severity?: 'low' | 'medium' | 'high' | 'critical'
  showDetails?: boolean
  className?: string
}

export default function ErrorDisplay({
  error,
  onRetry,
  onDismiss,
  severity = 'medium',
  showDetails = false,
  className = ''
}: ErrorDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(showDetails)
  
  const errorMessage = typeof error === 'string' ? error : error.message
  const errorStack = typeof error === 'object' && error.stack ? error.stack : null

  const getSeverityStyles = () => {
    switch (severity) {
      case 'critical':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          text: 'text-red-800',
          button: 'bg-red-100 text-red-700 hover:bg-red-200'
        }
      case 'high':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          icon: 'text-orange-600',
          text: 'text-orange-800',
          button: 'bg-orange-100 text-orange-700 hover:bg-orange-200'
        }
      case 'medium':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          text: 'text-yellow-800',
          button: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
        }
      case 'low':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'text-blue-600',
          text: 'text-blue-800',
          button: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          icon: 'text-gray-600',
          text: 'text-gray-800',
          button: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }
    }
  }

  const styles = getSeverityStyles()

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`${styles.bg} ${styles.border} border rounded-xl p-4 ${className}`}
    >
      <div className="flex items-start space-x-3">
        <AlertTriangle className={`w-5 h-5 ${styles.icon} mt-0.5 flex-shrink-0`} />
        
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium ${styles.text}`}>
            {errorMessage}
          </p>
          
          {errorStack && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700"
            >
              <span>Technical Details</span>
              {isExpanded ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>
          )}
          
          <AnimatePresence>
            {isExpanded && errorStack && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-3 overflow-hidden"
              >
                <div className="bg-gray-100 rounded-lg p-3 text-xs font-mono text-gray-800 overflow-auto max-h-32">
                  {errorStack}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        <div className="flex items-center space-x-2">
          {onRetry && (
            <button
              onClick={onRetry}
              className={`p-1.5 rounded-lg transition-colors ${styles.button}`}
              title="Retry"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
              title="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// Hook for managing errors
export function useErrorHandler() {
  const [errors, setErrors] = useState<Array<{
    id: string
    error: string | Error
    severity: 'low' | 'medium' | 'high' | 'critical'
    timestamp: Date
  }>>([])

  const addError = (error: string | Error, severity: 'low' | 'medium' | 'high' | 'critical' = 'medium') => {
    const id = Math.random().toString(36).substr(2, 9)
    setErrors(prev => [...prev, { id, error, severity, timestamp: new Date() }])
    return id
  }

  const removeError = (id: string) => {
    setErrors(prev => prev.filter(error => error.id !== id))
  }

  const clearAllErrors = () => {
    setErrors([])
  }

  return {
    errors,
    addError,
    removeError,
    clearAllErrors
  }
}
