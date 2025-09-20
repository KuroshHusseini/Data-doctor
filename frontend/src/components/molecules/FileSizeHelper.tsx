'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, FileText, Download, Scissors, Database } from 'lucide-react'

interface FileSizeHelperProps {
  fileSize: number
  maxSize: number
  onClose: () => void
}

export default function FileSizeHelper({ fileSize, maxSize, onClose }: FileSizeHelperProps) {
  const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2)
  const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(0)
  const reductionNeeded = ((fileSize - maxSize) / fileSize * 100).toFixed(0)

  const solutions = [
    {
      icon: <Scissors className="w-6 h-6 text-blue-600" />,
      title: "Split Your Data",
      description: "Divide your file into smaller chunks (e.g., by date range, region, or category)",
      steps: [
        "Open your file in Excel or a text editor",
        "Create separate files with 50,000-100,000 rows each",
        "Upload each file separately",
        "Combine results after processing"
      ]
    },
    {
      icon: <Database className="w-6 h-6 text-green-600" />,
      title: "Sample Your Data",
      description: "Use a representative sample for initial analysis",
      steps: [
        "Take a random sample of 10,000-50,000 rows",
        "Ensure the sample represents your full dataset",
        "Upload the sample for analysis",
        "Apply insights to your full dataset"
      ]
    },
    {
      icon: <FileText className="w-6 h-6 text-purple-600" />,
      title: "Optimize Your File",
      description: "Reduce file size by removing unnecessary data",
      steps: [
        "Remove columns you don't need for analysis",
        "Delete empty rows and columns",
        "Use CSV format instead of Excel if possible",
        "Compress the file if needed"
      ]
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-soft-lg overflow-hidden"
      >
        {/* Header */}
        <div className="bg-red-50 border-b border-red-200 p-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-red-900">File Too Large</h2>
              <p className="text-red-700">
                Your file ({fileSizeMB}MB) exceeds the {maxSizeMB}MB limit
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="mb-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-800 mb-2">Quick Summary</h3>
              <p className="text-yellow-700 text-sm">
                Your file is <strong>{reductionNeeded}% larger</strong> than the maximum allowed size. 
                Here are several ways to work with your data:
              </p>
            </div>
          </div>

          {/* Solutions */}
          <div className="space-y-6">
            {solutions.map((solution, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {solution.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {solution.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {solution.description}
                    </p>
                    <div className="space-y-2">
                      {solution.steps.map((step, stepIndex) => (
                        <div key={stepIndex} className="flex items-start space-x-2">
                          <span className="flex-shrink-0 w-5 h-5 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-xs font-medium">
                            {stepIndex + 1}
                          </span>
                          <span className="text-sm text-gray-700">{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Additional Help */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">Need More Help?</h3>
            <p className="text-blue-700 text-sm mb-3">
              If you're working with very large datasets regularly, consider:
            </p>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Using database connections for direct data access</li>
              <li>• Implementing data pipelines for automated processing</li>
              <li>• Contacting our support team for enterprise solutions</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 border-t border-gray-200 p-6">
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => {
                // Open help documentation
                window.open('https://docs.datadoctor.app/large-files', '_blank')
              }}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              View Documentation
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
