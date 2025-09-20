'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, X, RefreshCw } from 'lucide-react'
import ErrorToast from '../atoms/ErrorToast'
import { useErrorManager, ErrorInfo } from '../../hooks/useErrorManager'

interface ErrorDisplayProps {
  className?: string
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center'
}

export default function ErrorDisplay({ 
  className = '', 
  position = 'top-right' 
}: ErrorDisplayProps) {
  const { errors, removeError } = useErrorManager()

  const getPositionClasses = () => {
    switch (position) {
      case 'top-right':
        return 'top-4 right-4'
      case 'top-left':
        return 'top-4 left-4'
      case 'bottom-right':
        return 'bottom-4 right-4'
      case 'bottom-left':
        return 'bottom-4 left-4'
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2'
      default:
        return 'top-4 right-4'
    }
  }

  return (
    <div className={`fixed z-50 ${getPositionClasses()} ${className}`}>
      <div className="space-y-2">
        <AnimatePresence>
          {errors.map((error) => (
            <ErrorToast
              key={error.id}
              error={error}
              onDismiss={removeError}
              autoDismiss={error.type !== 'error'}
              duration={error.type === 'error' ? 8000 : 5000}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
