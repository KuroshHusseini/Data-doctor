#!/bin/bash

# Port cleanup script for Data Doctor

echo "🧹 Cleaning up ports for Data Doctor..."

# Kill processes on port 3000 (Frontend)
echo "🔧 Checking port 3000 (Frontend)..."
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "   Killing processes on port 3000..."
    lsof -ti:3000 | xargs kill -9
    echo "   ✅ Port 3000 freed"
else
    echo "   ✅ Port 3000 is already free"
fi

# Kill processes on port 8000 (Backend)
echo "🔧 Checking port 8000 (Backend)..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9
    echo "   ✅ Port 8000 freed"
else
    echo "   ✅ Port 8000 is already free"
fi

# Wait a moment for ports to be fully released
sleep 2

echo ""
echo "✅ Port cleanup complete!"
echo "🚀 You can now start the application with ./start.sh"