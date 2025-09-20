# Data Doctor Application - Setup Guide

## Prerequisites

Before setting up the Data Doctor Application, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **MongoDB** - [Download MongoDB](https://www.mongodb.com/try/download/community)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Optional but Recommended
- **MongoDB Compass** - [Download MongoDB Compass](https://www.mongodb.com/products/compass) (GUI for MongoDB)
- **VS Code** - [Download VS Code](https://code.visualstudio.com/)

## Quick Start

### 1. Clone and Setup
```bash
# Navigate to your project directory
cd "Junction two"

# Make the startup script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

### 2. Manual Setup (Alternative)

If you prefer to set up manually:

#### Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp backend/env.example backend/.env

# Edit the .env file and add your OpenAI API key
# MONGODB_URL=mongodb://localhost:27017
# OPENAI_API_KEY=your-openai-api-key-here

# Start MongoDB (if not already running)
# On macOS: brew services start mongodb-community
# On Ubuntu: sudo systemctl start mongod

# Start the backend
cd backend
python main.py
```

#### Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the frontend
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017

# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Development
PYTHON_ENV=development
```

### Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Usage

### 1. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 2. Upload Data
- Click "Choose a file or drag it here" to upload your dataset
- Supported formats: CSV, Excel (.xlsx, .xls), JSON
- Maximum file size: 100MB

### 3. Analyze Data Quality
- The system automatically analyzes your data for:
  - Missing values
  - Duplicates
  - Format inconsistencies
  - Data type mismatches
  - Statistical outliers

### 4. Apply Fixes
- Review detected issues
- Apply automated fixes with AI assistance
- View before/after comparisons

### 5. Download Clean Data
- Download the cleaned dataset
- Access data lineage and transformation history

### 6. Chat with AI
- Click the "AI Chat" button to interact with the Data Doctor AI
- Ask questions about your data issues and fixes
- Get intelligent recommendations

## Demo Data

A sample dataset (`demo_data.csv`) is included for testing. This dataset contains:
- 100 customer purchase records
- Various data quality issues (missing values, duplicates, format inconsistencies)
- Multiple product categories and price ranges

## Features

### Core Features
- ✅ **Flexible Data Input** - Support for CSV, Excel, JSON
- ✅ **Data Quality Detection** - Automatic issue identification
- ✅ **Automated Data Fixes** - Smart corrections with AI
- ✅ **AI-Driven Suggestions** - Intelligent recommendations
- ✅ **Anomaly Detection** - Statistical outlier detection
- ✅ **Uncertainty Identification** - Highlight uncertain fixes
- ✅ **Data Lineage** - Visual transformation history
- ✅ **Data Delivery** - Download cleaned datasets
- ✅ **Conversational AI** - Chat interface for questions
- ✅ **History Tracking** - View previous uploads

### Technical Features
- Modern React/Next.js frontend with Tailwind CSS
- FastAPI backend with async support
- MongoDB for data persistence
- OpenAI GPT integration for AI features
- Responsive design with Apple-inspired UI
- Real-time data processing
- Comprehensive error handling

## Troubleshooting

### Common Issues

#### MongoDB Connection Error
```
Error: Could not connect to MongoDB
```
**Solution**: Ensure MongoDB is running
- macOS: `brew services start mongodb-community`
- Ubuntu: `sudo systemctl start mongod`
- Windows: Start MongoDB service from Services

#### OpenAI API Error
```
Error: Invalid API key
```
**Solution**: 
1. Check your OpenAI API key in the `.env` file
2. Ensure you have credits in your OpenAI account
3. Verify the API key is correctly formatted

#### Port Already in Use
```
Error: Port 3000/8000 already in use
```
**Solution**:
- Kill processes using the ports: `lsof -ti:3000 | xargs kill -9`
- Or change ports in the configuration files

#### File Upload Issues
```
Error: File too large or unsupported format
```
**Solution**:
- Ensure file is under 100MB
- Use supported formats: CSV, Excel, JSON
- Check file encoding (UTF-8 recommended)

### Getting Help

1. Check the console logs for detailed error messages
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Check MongoDB connection and OpenAI API key

## Development

### Project Structure
```
data-doctor/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models.py           # Data models
│   ├── data_processor.py   # Data processing logic
│   ├── ai_service.py       # AI integration
│   └── temp/               # Temporary file storage
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   └── components/    # React components
│   └── package.json
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
└── README.md              # This file
```

### Adding New Features

1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create components in `src/components/`
3. **Data Processing**: Extend `data_processor.py`
4. **AI Features**: Enhance `ai_service.py`

### Testing

```bash
# Test backend
cd backend
python -m pytest

# Test frontend
cd frontend
npm test
```

## License

This project is for demonstration purposes. Please ensure you comply with all applicable licenses for the dependencies used.

## Support

For issues and questions:
1. Check this setup guide
2. Review the console logs
3. Verify all prerequisites are met
4. Ensure proper configuration

---

**Happy Data Cleaning! 🧹✨**
