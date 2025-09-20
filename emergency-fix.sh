#!/bin/bash

# Emergency Fix Script for Data Doctor Application
# Handles common setup issues and compatibility problems

echo "🚨 Emergency Fix Script for Data Doctor"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

echo "🔧 Fixing Python 3.12+ compatibility issues..."

# Remove existing virtual environment
if [ -d "venv" ]; then
    echo "   Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "   Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

# Upgrade pip, setuptools, and wheel first
echo "   Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install numpy and pandas with specific versions for Python 3.12+
echo "   Installing NumPy and Pandas with Python 3.12+ compatibility..."
pip install "numpy>=1.26.0" "pandas>=2.1.4" "scikit-learn>=1.3.2"

# Install other requirements
echo "   Installing other requirements..."
pip install -r requirements.txt

echo "✅ Python dependencies fixed!"

echo ""
echo "🔧 Fixing Node.js dependencies..."

# Go to frontend directory
cd frontend

# Remove node_modules and package-lock.json
if [ -d "node_modules" ]; then
    echo "   Removing existing node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "   Removing package-lock.json..."
    rm -f package-lock.json
fi

# Clear npm cache
echo "   Clearing npm cache..."
npm cache clean --force

# Install dependencies
echo "   Installing Node.js dependencies..."
npm install

# Fix any security vulnerabilities
echo "   Fixing security vulnerabilities..."
npm audit fix

echo "✅ Node.js dependencies fixed!"

# Go back to root directory
cd ..

echo ""
echo "🔧 Setting up environment files..."

# Create backend .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "   Creating backend/.env file..."
    cp backend/env.example backend/.env
    echo "   ⚠️  Please edit backend/.env and add your OpenAI API key"
fi

# Create necessary directories
echo "   Creating necessary directories..."
mkdir -p backend/temp
mkdir -p backend/cleaned

echo "✅ Environment setup completed!"

echo ""
echo "🎉 Emergency fix completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start MongoDB if not already running"
echo "3. Run ./start.sh to start the application"
echo ""
echo "If you still encounter issues, please check:"
echo "- Python version (3.8+ required)"
echo "- Node.js version (16+ required)"
echo "- MongoDB is running"
echo "- OpenAI API key is valid"