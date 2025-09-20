'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, X, Bot, User, Loader } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface ChatInterfaceProps {
  onClose: () => void
  uploadData?: any
  analysisData?: any
  fixData?: any
}

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
}

export default function ChatInterface({ onClose, uploadData, analysisData, fixData }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your Data Doctor AI assistant. I can help you understand your data issues, explain fixes, and provide insights. What would you like to know?",
      sender: 'ai',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load chat history when component mounts
  useEffect(() => {
    const loadChatHistory = async () => {
      if (!uploadData?.upload_id) return

      try {
        const response = await axios.get(`http://localhost:8000/chat/${uploadData.upload_id}/history`)
        const conversations = response.data.conversations || []
        
        const historyMessages: Message[] = []
        conversations.forEach((conv: any) => {
          // Add user message
          historyMessages.push({
            id: `user_${conv._id}`,
            content: conv.user_message,
            sender: 'user',
            timestamp: new Date(conv.timestamp)
          })
          
          // Add AI response
          historyMessages.push({
            id: `ai_${conv._id}`,
            content: conv.ai_response,
            sender: 'ai',
            timestamp: new Date(conv.timestamp)
          })
        })
        
        if (historyMessages.length > 0) {
          setMessages(prev => [...prev, ...historyMessages])
        }
      } catch (error) {
        console.error('Failed to load chat history:', error)
        // Don't show error to user, just continue with empty chat
      }
    }

    loadChatHistory()
  }, [uploadData?.upload_id])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const messageContent = inputValue
    setInputValue('')
    setIsLoading(true)

    try {
      // Get the current upload ID from context
      const uploadId = uploadData?.upload_id || 'demo'
      
      const response = await axios.post(`http://localhost:8000/chat/${uploadId}`, {
        content: messageContent
      }, {
        timeout: 30000 // 30 second timeout
      })

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        sender: 'ai',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error: any) {
      console.error('Chat error:', error)
      
      let errorMessage = "I'm sorry, I'm having trouble processing your request right now. Please try again."
      
      if (error.response?.status === 404) {
        errorMessage = "No data found for this upload. Please upload a file first."
      } else if (error.response?.status === 500) {
        const errorData = error.response.data
        if (errorData?.message) {
          errorMessage = errorData.message
        }
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = "Request timed out. The AI is taking longer than expected to respond."
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = "Network error. Please check your connection and try again."
      }
      
      toast.error('Failed to send message. Please try again.')
      
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessage,
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickQuestions = [
    "What issues were found in my data?",
    "Explain the fixes that were applied",
    "What's the quality score?",
    "Show me the uncertain fields",
    "Why did that anomaly happen?"
  ]

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
        className="relative w-full max-w-2xl h-[600px] bg-white rounded-2xl shadow-soft-lg flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Data Doctor AI</h3>
              <p className="text-sm text-gray-500">Your intelligent data assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex items-start space-x-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.sender === 'user' 
                      ? 'bg-primary-600 text-white' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {message.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`px-4 py-2 rounded-2xl ${
                    message.sender === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.sender === 'user' ? 'text-primary-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="flex items-start space-x-2">
                <div className="w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="px-4 py-2 rounded-2xl bg-gray-100">
                  <div className="flex items-center space-x-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-sm text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="px-4 pb-2">
            <p className="text-sm text-gray-500 mb-2">Quick questions:</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(question)}
                  className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-end space-x-2">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your data..."
                className="w-full px-4 py-2 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows={1}
                style={{ minHeight: '40px', maxHeight: '120px' }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="p-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
