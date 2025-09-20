# 🩺 Data Doctor

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0-black.svg)](https://nextjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **An intelligent system that detects, fixes, and delivers clean, reliable data to users with AI-powered assistance.**

Data Doctor is a comprehensive data quality management platform that automatically identifies data issues, applies intelligent fixes, and provides conversational AI guidance throughout the data cleaning process.

## ✨ Features

### 🔍 **Intelligent Data Analysis**

- **Flexible Data Input** - Support for CSV, Excel (.xlsx, .xls), JSON formats
- **Automatic Quality Detection** - Missing values, duplicates, format inconsistencies
- **Statistical Anomaly Detection** - Outlier identification using machine learning
- **Data Type Validation** - Automatic schema inference and validation
- **Pattern Recognition** - Smart detection of date formats, email patterns, phone numbers

### 🤖 **AI-Powered Assistance**

- **Conversational Interface** - Chat with AI about your data issues
- **Intelligent Recommendations** - Context-aware suggestions for data fixes
- **Uncertainty Identification** - Highlights areas requiring manual review
- **Natural Language Explanations** - Easy-to-understand fix descriptions

### 🛠️ **Automated Data Fixes**

- **Smart Corrections** - Preserves data integrity while fixing issues
- **Batch Processing** - Apply fixes to large datasets efficiently
- **Before/After Comparisons** - Visual diff of applied changes
- **Rollback Capability** - Undo fixes if needed
- **Custom Rules** - Define your own data quality rules

### 📊 **Data Management & Insights**

- **Data Lineage Tracking** - Complete history of transformations
- **Quality Scoring** - Numerical assessment of data quality
- **Root Cause Analysis** - Trace problems back to their source
- **Export & Integration** - Download cleaned data or integrate with pipelines
- **History Management** - Access previously cleaned datasets

### 🚀 **Enhanced Performance & Reliability**

- **Large File Support** - Process files up to 100MB with chunked processing
- **Upload Management** - Cancel ongoing uploads or replace files seamlessly
- **Progress Tracking** - Real-time progress indicators for all operations
- **Error Recovery** - Automatic retries and graceful error handling
- **Memory Optimization** - Efficient processing of large datasets
- **Parallel Processing** - Multi-threaded analysis for faster results

## 🎯 Use Case Example

**Scenario**: A Marketing Data Analyst uploads customer purchase records from multiple sources.

**Data Doctor automatically**:

- ✅ Detects 45 missing customer IDs
- ✅ Identifies 120 duplicate entries
- ✅ Standardizes 3 different date formats
- ✅ Corrects anomalous $9999 transaction to $99.99
- ✅ Provides AI explanations for each fix
- ✅ Delivers clean dataset ready for BI tools

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **MongoDB** - [Download](https://www.mongodb.com/try/download/community)

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd "Junction two"

# Make startup script executable and run
chmod +x start.sh
./start.sh
```

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

```bash
# Create virtual environment (in backend folder)
python3 -m venv backend/.venv
source backend/.venv/bin/activate  # Windows: backend\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp backend/env.example backend/.env
# Edit backend/.env and add your OpenAI API key

# Start MongoDB
# macOS: brew services start mongodb-community
# Ubuntu: sudo systemctl start mongod

# Start backend
cd backend && python main.py
```

#### Frontend Setup

```bash
# Install Node.js dependencies
cd frontend && npm install

# Start development server
npm run dev
```

</details>

## 🖥️ Application Access

| Service               | URL                        | Description                |
| --------------------- | -------------------------- | -------------------------- |
| **Frontend**          | http://localhost:3000      | Main application interface |
| **Backend API**       | http://localhost:8000      | REST API endpoints         |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs       |

## � **Quick Fix for Setup Issues**

If you encounter Python 3.12+ compatibility or npm security issues:

```bash
# For Python/NumPy issues
./emergency-fix.sh

# For npm vulnerabilities
./npm-fix.sh

# For complete clean setup
./fix-setup.sh
```

## �🎬 Screenshots

### Data Upload Interface

_Clean, intuitive drag-and-drop interface for file uploads_

### Quality Analysis Dashboard

_Comprehensive overview of detected data issues with severity indicators_

### AI Chat Interface

_Conversational AI assistant providing data insights and recommendations_

### Data Lineage View

_Visual timeline of all transformations and fixes applied to your data_

> 📝 **Note**: Screenshots will be added in future releases

## 🏗️ Tech Stack

### Frontend

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Sass with BEM methodology + Tailwind CSS
- **Architecture**: Atomic Design Pattern
- **State Management**: React Context API
- **Charts**: Recharts for data visualization

### Backend

- **Framework**: FastAPI with async support
- **Database**: MongoDB with Motor (async driver)
- **AI Integration**: OpenAI GPT-3.5/4 for conversational features
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **File Handling**: Support for CSV, Excel, JSON

### Infrastructure

- **Environment**: Python virtual environments
- **Development**: Hot reload for both frontend and backend
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Error Handling**: Comprehensive logging and error reporting

## 📁 Project Structure

```
data-doctor/
├── 📁 frontend/              # Next.js React application
│   ├── 📁 src/
│   │   ├── 📁 app/          # App router pages
│   │   └── 📁 components/   # Atomic design components
│   │       ├── 📁 atoms/    # Basic UI elements
│   │       └── 📁 molecules/ # Composed components
│   ├── 📄 package.json
│   └── 📄 globals.scss      # SCSS with BEM methodology
├── 📁 backend/              # FastAPI Python application
│   ├── 📄 main.py          # FastAPI application entry
│   ├── 📄 models.py        # Pydantic data models
│   ├── 📄 data_processor.py # Data quality analysis engine
│   ├── 📄 ai_service.py    # OpenAI integration service
│   └── 📁 temp/           # Temporary file storage
├── 📄 requirements.txt     # Python dependencies
├── 📄 demo_data.csv       # Sample dataset for testing
├── 📄 start.sh           # One-command startup script
└── 📄 README.md          # This file
```

## 🔧 Configuration

### Environment Variables

Create `backend/.env` with:

```env
# Database
MONGODB_URL=mongodb://localhost:27017

# AI Services (Required for chat features)
OPENAI_API_KEY=your-openai-api-key-here

# Development
PYTHON_ENV=development
```

### Getting OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account or sign in
3. Navigate to API Keys section
4. Generate new secret key
5. Add to your `.env` file

## 📖 Usage Guide

### 1. **Upload Your Data**

- Drag & drop or browse for files
- Supports CSV, Excel (.xlsx, .xls), JSON
- Maximum file size: 100MB

### 2. **Review Quality Analysis**

- Automatic scanning for common issues
- Severity classification (Low/Medium/High/Critical)
- Statistical summaries and recommendations

### 3. **Apply Intelligent Fixes**

- Review AI-suggested corrections
- Apply fixes individually or in bulk
- View before/after comparisons

### 4. **Chat with AI Assistant**

- Ask questions about detected issues
- Get explanations for recommended fixes
- Receive data quality best practices

### 5. **Download Clean Data**

- Export cleaned dataset in original format
- Access detailed transformation reports
- Download data lineage documentation

## 🧪 Demo Data

Included `demo_data.csv` contains:

- **100 customer purchase records**
- **Intentional data quality issues** for testing:
  - Missing values in various columns
  - Duplicate customer records
  - Inconsistent date formats
  - Price anomalies and outliers
  - Mixed case inconsistencies

Perfect for exploring Data Doctor's capabilities!

## 🛠️ Development

### Adding New Data Quality Rules

```python
# In data_processor.py
def detect_custom_issue(self, df):
    """Add your custom data quality detection logic"""
    issues = []
    # Your detection logic here
    return issues
```

### Extending AI Capabilities

```python
# In ai_service.py
def custom_ai_analysis(self, data_context):
    """Extend AI analysis with custom prompts"""
    # Your AI logic here
    pass
```

### Frontend Component Development

Follow Atomic Design principles:

- **Atoms**: Basic UI elements (buttons, inputs)
- **Molecules**: Composed components (search bars, cards)
- **Organisms**: Complex components (headers, data tables)

## 🐛 Troubleshooting

<details>
<summary><strong>Common Issues & Solutions</strong></summary>

### Python 3.12+ Compatibility Issues

**Error**: `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'` or NumPy build failures

**Solution**:

```bash
# Use the emergency fix script
./emergency-fix.sh

# Or manual fix
source backend/.venv/bin/activate
pip install "numpy>=1.26.0" "pandas>=2.1.4" "scikit-learn>=1.3.2"
```

**Error**: `ModuleNotFoundError: No module named 'distutils'`

**Solution**:

```bash
# Upgrade pip and install setuptools
pip install --upgrade pip setuptools wheel

# Reinstall requirements
pip install -r requirements.txt
```

### MongoDB Connection Error

```bash
# Ensure MongoDB is running
brew services start mongodb-community  # macOS
sudo systemctl start mongod           # Ubuntu
```

### Python Dependencies Installation Failed

**Solution**:

```bash
# Clean virtual environment and start fresh
rm -rf backend/.venv
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Next.js Configuration Warnings

**Warning**: `Invalid next.config.js options detected: Unrecognized key(s) in object: 'appDir'`

**Solution**: This has been fixed in the latest version. The `appDir` experimental flag is no longer needed in Next.js 14.

### Port Already in Use

```bash
# Kill processes on occupied ports
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
```

### OpenAI API Issues

- Verify API key in `.env` file
- Check OpenAI account credits
- Ensure key format is correct

### File Upload Problems

- Confirm file size < 100MB
- Check file format (CSV, Excel, JSON)
- Verify file encoding (UTF-8 recommended)

### npm Security Vulnerabilities

```bash
# Use the npm fix script
./npm-fix.sh

# Or manual fix
cd frontend
npm audit fix

# If issues persist, try force fix (use with caution)
npm audit fix --force
```

### Backend Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:

```bash
# Ensure virtual environment is activated
source backend/.venv/bin/activate

# Check if packages are installed
pip list | grep fastapi

# If not installed, reinstall
pip install -r requirements.txt
```

</details>

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT API powering our AI features
- **FastAPI** for the excellent async Python framework
- **Next.js** for the robust React framework
- **MongoDB** for flexible document storage
- **Scikit-learn** for machine learning capabilities

## 📞 Support

- 📧 **Email**: support@datadoctor.app
- 💬 **Discord**: [Join our community](https://discord.gg/datadoctor)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/data-doctor/issues)
- 📖 **Documentation**: [Full Docs](https://docs.datadoctor.app)

---

<div align="center">

**[⭐ Star this repository](https://github.com/your-org/data-doctor)** if Data Doctor helped you!

Made with ❤️ by the Data Doctor Team

</div>
