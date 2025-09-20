'use client'

import { useState, useCallback } from 'react'

export interface ErrorInfo {
  id: string
  message: string
  type: 'error' | 'warning' | 'info'
  details?: string
  action?: {
    label: string
    onClick: () => void
  }
  timestamp: Date
}

export function useErrorManager() {
  const [errors, setErrors] = useState<ErrorInfo[]>([])

  const addError = useCallback((
    message: string,
    type: 'error' | 'warning' | 'info' = 'error',
    details?: string,
    action?: { label: string; onClick: () => void }
  ) => {
    const error: ErrorInfo = {
      id: Math.random().toString(36).substr(2, 9),
      message,
      type,
      details,
      action,
      timestamp: new Date()
    }
    
    setErrors(prev => [...prev, error])
    return error.id
  }, [])

  const removeError = useCallback((id: string) => {
    setErrors(prev => prev.filter(error => error.id !== id))
  }, [])

  const clearAllErrors = useCallback(() => {
    setErrors([])
  }, [])

  const clearErrorsByType = useCallback((type: 'error' | 'warning' | 'info') => {
    setErrors(prev => prev.filter(error => error.type !== type))
  }, [])

  const getErrorsByType = useCallback((type: 'error' | 'warning' | 'info') => {
    return errors.filter(error => error.type === type)
  }, [errors])

  const hasErrors = errors.length > 0
  const errorCount = errors.filter(e => e.type === 'error').length
  const warningCount = errors.filter(e => e.type === 'warning').length
  const infoCount = errors.filter(e => e.type === 'info').length

  return {
    errors,
    addError,
    removeError,
    clearAllErrors,
    clearErrorsByType,
    getErrorsByType,
    hasErrors,
    errorCount,
    warningCount,
    infoCount
  }
}
