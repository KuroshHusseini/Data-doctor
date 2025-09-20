'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, X, RefreshCw, Info } from 'lucide-react'
import { useState } from 'react'

interface ErrorToastProps {
  error: {
    id: string
    message: string
    type: 'error' | 'warning' | 'info'
    details?: string
    action?: {
      label: string
      onClick: () => void
    }
  }
  onDismiss: (id: string) => void
  autoDismiss?: boolean
  duration?: number
}

export default function ErrorToast({ 
  error, 
  onDismiss, 
  autoDismiss = true, 
  duration = 5000 
}: ErrorToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  const handleDismiss = () => {
    setIsVisible(false)
    setTimeout(() => onDismiss(error.id), 300)
  }

  const getIcon = () => {
    switch (error.type) {
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      case 'info':
        return <Info className="w-5 h-5 text-blue-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-red-600" />
    }
  }

  const getBgColor = () => {
    switch (error.type) {
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
      case 'info':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
      default:
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
    }
  }

  const getTextColor = () => {
    switch (error.type) {
      case 'error':
        return 'text-red-800 dark:text-red-200'
      case 'warning':
        return 'text-yellow-800 dark:text-yellow-200'
      case 'info':
        return 'text-blue-800 dark:text-blue-200'
      default:
        return 'text-red-800 dark:text-red-200'
    }
  }

  // Auto dismiss
  useState(() => {
    if (autoDismiss) {
      const timer = setTimeout(() => {
        handleDismiss()
      }, duration)
      return () => clearTimeout(timer)
    }
  })

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ duration: 0.3 }}
          className={`glass-effect p-4 rounded-xl border ${getBgColor()} shadow-lg max-w-md`}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {getIcon()}
            </div>
            
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${getTextColor()}`}>
                {error.message}
              </p>
              
              {error.details && (
                <p className={`text-xs mt-1 ${getTextColor()} opacity-75`}>
                  {error.details}
                </p>
              )}
              
              {error.action && (
                <button
                  onClick={error.action.onClick}
                  className="mt-2 text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
                >
                  {error.action.label}
                </button>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              {error.action && (
                <button
                  onClick={error.action.onClick}
                  className="p-1 hover:bg-white/20 dark:hover:bg-gray-800/20 rounded transition-colors"
                  title="Retry"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              )}
              
              <button
                onClick={handleDismiss}
                className="p-1 hover:bg-white/20 dark:hover:bg-gray-800/20 rounded transition-colors"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
