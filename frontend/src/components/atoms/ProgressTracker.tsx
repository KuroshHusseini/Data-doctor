'use client'

import { motion } from 'framer-motion'
import { CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface ProgressStep {
  id: string
  label: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  description?: string
  progress?: number
}

interface ProgressTrackerProps {
  steps: ProgressStep[]
  currentStep?: string
  className?: string
}

export default function ProgressTracker({ steps, currentStep, className = '' }: ProgressTrackerProps) {
  const getStepIcon = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-600" />
      case 'in_progress':
        return (
          <div className="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
        )
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStepStyles = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return {
          bg: 'bg-success-600',
          text: 'text-success-600',
          border: 'border-success-600'
        }
      case 'in_progress':
        return {
          bg: 'bg-primary-600',
          text: 'text-primary-600',
          border: 'border-primary-600'
        }
      case 'error':
        return {
          bg: 'bg-red-600',
          text: 'text-red-600',
          border: 'border-red-600'
        }
      default:
        return {
          bg: 'bg-gray-300',
          text: 'text-gray-400',
          border: 'border-gray-300'
        }
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {steps.map((step, index) => {
        const styles = getStepStyles(step)
        const isLast = index === steps.length - 1
        
        return (
          <div key={step.id} className="flex items-start space-x-4">
            {/* Step Icon */}
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full border-2 ${styles.border} ${styles.bg} flex items-center justify-center`}>
                {getStepIcon(step)}
              </div>
              
              {/* Connecting Line */}
              {!isLast && (
                <div className={`w-0.5 h-8 mt-2 ${step.status === 'completed' ? 'bg-success-600' : 'bg-gray-300'}`} />
              )}
            </div>
            
            {/* Step Content */}
            <div className="flex-1 min-w-0 pb-8">
              <div className="flex items-center justify-between">
                <h3 className={`text-sm font-medium ${styles.text}`}>
                  {step.label}
                </h3>
                
                {step.status === 'in_progress' && step.progress !== undefined && (
                  <span className="text-xs text-gray-500">
                    {Math.round(step.progress)}%
                  </span>
                )}
              </div>
              
              {step.description && (
                <p className="text-sm text-gray-600 mt-1">
                  {step.description}
                </p>
              )}
              
              {/* Progress Bar for in-progress steps */}
              {step.status === 'in_progress' && step.progress !== undefined && (
                <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                  <motion.div
                    className="bg-primary-600 h-1.5 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${step.progress}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  />
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Hook for managing progress
export function useProgressTracker(initialSteps: Omit<ProgressStep, 'status'>[]) {
  const [steps, setSteps] = useState<ProgressStep[]>(
    initialSteps.map(step => ({ ...step, status: 'pending' as const }))
  )

  const updateStep = (stepId: string, updates: Partial<ProgressStep>) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, ...updates } : step
    ))
  }

  const setStepStatus = (stepId: string, status: ProgressStep['status']) => {
    updateStep(stepId, { status })
  }

  const setStepProgress = (stepId: string, progress: number) => {
    updateStep(stepId, { progress, status: 'in_progress' })
  }

  const completeStep = (stepId: string) => {
    updateStep(stepId, { status: 'completed', progress: 100 })
  }

  const errorStep = (stepId: string, error?: string) => {
    updateStep(stepId, { 
      status: 'error', 
      description: error || 'An error occurred'
    })
  }

  const resetSteps = () => {
    setSteps(prev => prev.map(step => ({ 
      ...step, 
      status: 'pending' as const,
      progress: undefined
    })))
  }

  const getCurrentStep = () => {
    return steps.find(step => step.status === 'in_progress') || 
           steps.find(step => step.status === 'pending')
  }

  const getCompletedSteps = () => {
    return steps.filter(step => step.status === 'completed')
  }

  const getProgressPercentage = () => {
    const completedSteps = getCompletedSteps().length
    return (completedSteps / steps.length) * 100
  }

  return {
    steps,
    updateStep,
    setStepStatus,
    setStepProgress,
    completeStep,
    errorStep,
    resetSteps,
    getCurrentStep,
    getCompletedSteps,
    getProgressPercentage
  }
}
