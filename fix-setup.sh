#!/bin/bash

# Data Doctor - Clean Setup Script
# This script fixes common setup issues

echo "🧹 Data Doctor - Clean Setup & Fix Script"
echo "=========================================="

# Check current directory
if [ ! -f "start.sh" ]; then
    echo "❌ Please run this script from the Data Doctor root directory"
    exit 1
fi

# 1. Clean and recreate Python virtual environment
echo "🐍 Setting up Python environment..."
if [ -d "venv" ]; then
    echo "   Removing existing virtual environment..."
    rm -rf venv
fi

echo "   Creating new virtual environment..."
python3 -m venv backend/.venv
source backend/.venv/bin/activate

echo "   Upgrading pip and essential tools..."
pip install --upgrade pip setuptools wheel

echo "   Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "   ⚠️  Some packages failed to install. Trying alternative approach..."
    echo "   Installing packages individually with latest compatible versions..."
    
    # Install core packages first
    pip install "fastapi==0.104.1" "uvicorn[standard]==0.24.0" "pydantic==2.5.0"
    
    # Install database packages
    pip install "pymongo==4.6.0" "motor==3.3.2"
    
    # Install data processing with latest compatible versions
    pip install "numpy>=1.26.0" "pandas>=2.1.4" "openpyxl==3.1.2"
    pip install "scikit-learn>=1.3.2" "scipy>=1.11.4"
    
    # Install remaining packages
    pip install "openai==1.3.7" "python-multipart==0.0.6" "aiofiles==23.2.1" "httpx==0.25.2"
    pip install "python-jose[cryptography]==3.3.0" "passlib[bcrypt]==1.7.4" "python-dotenv==1.0.0"
    pip install "jinja2==3.1.2" "xlrd==2.0.1" "python-dateutil==2.8.2"
    pip install "pytest==7.4.3" "pytest-asyncio==0.21.1"
fi

# 2. Fix Node.js dependencies and vulnerabilities
echo ""
echo "📦 Setting up Node.js environment..."
cd frontend

echo "   Cleaning npm cache..."
npm cache clean --force

echo "   Removing node_modules and package-lock.json..."
rm -rf node_modules package-lock.json

echo "   Installing Node.js dependencies..."
npm install

echo "   Fixing npm vulnerabilities..."
npm audit fix

# If there are still critical vulnerabilities, try force fix
if npm audit | grep -q "critical"; then
    echo "   ⚠️  Critical vulnerabilities found. Attempting force fix..."
    echo "   (This may update packages to newer versions)"
    npm audit fix --force
fi

cd ..

# 3. Create necessary directories
echo ""
echo "📁 Creating project directories..."
mkdir -p backend/temp
mkdir -p backend/cleaned

# 4. Setup environment file
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "   ✅ Created backend/.env from example"
        echo "   📝 Please edit backend/.env and add your OpenAI API key"
    else
        echo "   ❌ backend/.env.example not found"
    fi
else
    echo "   ✅ backend/.env already exists"
fi

# 5. Check MongoDB
echo ""
echo "🍃 Checking MongoDB..."
if pgrep -x "mongod" > /dev/null; then
    echo "   ✅ MongoDB is running"
else
    echo "   ⚠️  MongoDB is not running"
    echo "   To start MongoDB:"
    echo "   macOS: brew services start mongodb-community"
    echo "   Ubuntu: sudo systemctl start mongod"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "   ./start.sh"
echo ""
echo "Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"