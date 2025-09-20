#!/bin/bash

# Data Doctor Application Startup Script

echo "🚀 Starting Data Doctor Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Load NVM if available
if [ -f ~/.nvm/nvm.sh ]; then
    source ~/.nvm/nvm.sh
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB first."
    echo "   On macOS: brew services start mongodb-community"
    echo "   On Ubuntu: sudo systemctl start mongod"
    echo "   Or start MongoDB manually and run this script again."
    exit 1
fi

# Clean up any existing processes on our ports
echo "🧹 Cleaning up ports..."
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "   Killing existing processes on port 3000..."
    lsof -ti:3000 | xargs kill -9
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   Killing existing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9
fi

# Wait for ports to be released
sleep 2

# Create virtual environment if it doesn't exist (inside backend folder)
if [ ! -d "backend/.venv" ]; then
    echo "📦 Creating Python virtual environment in backend folder..."
    python3 -m venv backend/.venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source backend/.venv/bin/activate

# Upgrade pip first to avoid compatibility issues
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/temp
mkdir -p backend/cleaned

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp backend/env.example backend/.env
    echo "📝 Please edit backend/.env and add your OpenAI API key"
fi

# Start the backend
echo "🔧 Starting FastAPI backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start the frontend
echo "🎨 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Data Doctor Application is starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
