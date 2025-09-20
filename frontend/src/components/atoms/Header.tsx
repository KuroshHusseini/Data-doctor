'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, History, Menu, X } from 'lucide-react'

interface HeaderProps {
  onChatClick: () => void
  onHistoryClick: () => void
}

export default function Header({ onChatClick, onHistoryClick }: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 glass-effect border-b border-white/20">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center space-x-3"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">DD</span>
            </div>
            <span className="text-xl font-bold text-gradient">Data Doctor</span>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <button
              onClick={onChatClick}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200"
            >
              <MessageCircle className="w-5 h-5" />
              <span>AI Chat</span>
            </button>
            <button
              onClick={onHistoryClick}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200"
            >
              <History className="w-5 h-5" />
              <span>History</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-white/20 transition-all duration-200"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden border-t border-white/20 py-4"
          >
            <div className="flex flex-col space-y-2">
              <button
                onClick={() => {
                  onChatClick()
                  setIsMobileMenuOpen(false)
                }}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200"
              >
                <MessageCircle className="w-5 h-5" />
                <span>AI Chat</span>
              </button>
              <button
                onClick={() => {
                  onHistoryClick()
                  setIsMobileMenuOpen(false)
                }}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200"
              >
                <History className="w-5 h-5" />
                <span>History</span>
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </header>
  )
}
