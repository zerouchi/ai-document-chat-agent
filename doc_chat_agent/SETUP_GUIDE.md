# AI Document Chat Agent - Complete Setup Guide

This comprehensive guide will walk you through setting up the AI Document Chat Agent from scratch, including all dependencies, configuration, and troubleshooting.

## 📋 Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation Steps](#2-installation-steps)
3. [Configuration Guide](#3-configuration-guide)
4. [Running the Application](#4-running-the-application)
5. [Verification & Testing](#5-verification--testing)
6. [Troubleshooting](#6-troubleshooting)
7. [Production Deployment](#7-production-deployment)
8. [Maintenance & Updates](#8-maintenance--updates)

---

## 1. System Requirements

### 1.1 Hardware Requirements

**Minimum Requirements:**
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB (8 GB recommended)
- **Storage**: 2 GB free space (more for documents and models)
- **Network**: Internet connection for Azure OpenAI (optional)

**Recommended Requirements:**
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB (16 GB for large document collections)
- **Storage**: 10+ GB SSD
- **Network**: Stable broadband connection

### 1.2 Software Requirements

**Operating System:**
- ✅ **Linux** (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- ✅ **macOS** (10.15+)
- ✅ **Windows** (10/11 with WSL2 recommended)

**Required Software:**
- **Python 3.8+** (Python 3.11 recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

**Optional but Recommended:**
- **Virtual Environment** (venv, conda, or virtualenv)
- **Docker** (for containerized deployment)
- **VS Code** or **PyCharm** (for development)

---

## 2. Installation Steps

### 2.1 Install Python and Dependencies

#### On Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-pip python3.11-venv git -y

# Verify installation
python3.11 --version
pip3.11 --version
```

#### On macOS:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11 git

# Verify installation
python3.11 --version
pip3.11 --version
```

#### On Windows:
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Install Git from [git-scm.com](https://git-scm.com/download/win)
4. Open Command Prompt or PowerShell and verify:
```cmd
python --version
pip --version
git --version
```

### 2.2 Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd Doc_chat_ai_agent

# Verify the project structure
ls -la
```

Expected output:
```
drwxr-xr-x  app/
drwxr-xr-x  static/
drwxr-xr-x  templates/
-rw-r--r--  requirements.txt
-rw-r--r--  run.py
-rw-r--r--  env.example
-rw-r--r--  README.md
```

### 2.3 Create Virtual Environment

#### Using venv (Recommended):
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python  # Should point to venv/bin/python
```

#### Using conda:
```bash
# Create conda environment
conda create -n doc-chat-agent python=3.11 -y

# Activate environment
conda activate doc-chat-agent
```

### 2.4 Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected key packages:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- openai==1.3.7
- faiss-cpu==1.7.4
- sentence-transformers==2.7.0

---

## 3. Configuration Guide

### 3.1 Environment Variables Setup

```bash
# Copy the example environment file
cp env.example .env

# Edit the configuration file
nano .env  # or use your preferred editor
```

### 3.2 Configuration Options

#### 3.2.1 Azure OpenAI Configuration (Optional)

If you have Azure OpenAI access:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_MODEL_NAME=gpt-4
```

**How to get Azure OpenAI credentials:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Create or navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the API key and endpoint
5. Note your deployment name from the "Model deployments" section

#### 3.2.2 Application Configuration

```env
# Application Configuration
UPLOAD_DIR=uploads
VECTOR_STORE_DIR=vector_store
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Performance Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOKENIZERS_PARALLELISM=false
```

#### 3.2.3 Local-Only Configuration

If you don't have Azure OpenAI, the application will work with local embeddings:

```env
# Minimal configuration for local operation
UPLOAD_DIR=uploads
VECTOR_STORE_DIR=vector_store
MAX_FILE_SIZE=10485760
TOKENIZERS_PARALLELISM=false
```

### 3.3 Directory Structure Creation

The application will create necessary directories automatically, but you can create them manually:

```bash
# Create required directories
mkdir -p uploads vector_store logs

# Set appropriate permissions (Linux/macOS)
chmod 755 uploads vector_store logs
```

---

## 4. Running the Application

### 4.1 Development Mode

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run the application
python run.py
```

Expected output:
```
🚀 Starting AI Document Chat Agent...
📍 Server will be available at: http://0.0.0.0:8000
📚 API Documentation: http://0.0.0.0:8000/api/docs
🔧 Make sure to configure your .env file with Azure OpenAI credentials
✅ Using local embeddings (dimension: 384)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.2 Alternative Startup Methods

#### Using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Using Python module:
```bash
python -m uvicorn app.main:app --reload
```

### 4.3 Background Mode (Linux/macOS)

```bash
# Run in background
nohup python run.py > app.log 2>&1 &

# Check if running
ps aux | grep python

# View logs
tail -f app.log

# Stop the application
pkill -f "python run.py"
```

---

## 5. Verification & Testing

### 5.1 Health Check

Open your browser and navigate to:
- **Main Application**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/api/docs

Expected health check response:
```json
{
  "status": "healthy",
  "service": "AI Document Chat Agent",
  "version": "1.0.0"
}
```

### 5.2 Upload Test

1. **Prepare Test Document**: Create a simple text file:
```bash
echo "This is a test document for the AI Document Chat Agent. It contains sample content for testing the upload and processing functionality." > test_document.txt
```

2. **Upload via Web Interface**:
   - Go to http://localhost:8000
   - Drag and drop `test_document.txt` onto the upload area
   - Verify successful upload message

3. **Upload via API**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_document.txt"
```

### 5.3 Chat Test

1. **Via Web Interface**:
   - Type a question like "What is this document about?"
   - Verify you receive a response

2. **Via API**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is this document about?",
       "conversation_id": null
     }'
```

### 5.4 Statistics Check

Visit http://localhost:8000/api/v1/stats to see system statistics:
```json
{
  "total_documents": 1,
  "total_chunks": 1,
  "total_conversations": 1,
  "vector_store_size": 1,
  "embedding_type": "local"
}
```

---

## 6. Troubleshooting

### 6.1 Common Installation Issues

#### Issue: Python version conflicts
```bash
# Error: "python: command not found" or wrong version
# Solution: Use specific Python version
python3.11 -m venv venv
# or
/usr/bin/python3.11 -m venv venv
```

#### Issue: pip installation failures
```bash
# Error: "Failed building wheel for faiss-cpu"
# Solution: Install system dependencies

# On Ubuntu/Debian:
sudo apt install build-essential python3-dev

# On CentOS/RHEL:
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# On macOS:
xcode-select --install
```

#### Issue: Permission denied errors
```bash
# Error: Permission denied when creating directories
# Solution: Check permissions and ownership
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### 6.2 Runtime Issues

#### Issue: Port already in use
```bash
# Error: "Address already in use"
# Solution: Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
# or use different port
python run.py --port 8001
```

#### Issue: Azure OpenAI connection failures
```
⚠️  Azure OpenAI connection failed: Invalid API key
```
**Solutions:**
1. Verify API key in `.env` file
2. Check endpoint URL format
3. Ensure deployment name is correct
4. Verify Azure OpenAI service is active

#### Issue: Local embeddings download failures
```
⚠️  Failed to load local embeddings: HTTP Error 403
```
**Solutions:**
1. Check internet connection
2. Clear Hugging Face cache: `rm -rf ~/.cache/huggingface/`
3. Set HF_HUB_DISABLE_SYMLINKS_WARNING=1
4. Try manual model download

#### Issue: File upload failures
```
❌ Upload failed: File too large
```
**Solutions:**
1. Check file size (default limit: 10MB)
2. Increase MAX_FILE_SIZE in `.env`
3. Verify file format (PDF, DOCX, TXT only)

### 6.3 Performance Issues

#### Issue: Slow document processing
**Solutions:**
1. Reduce chunk size in configuration
2. Increase system memory
3. Use SSD storage
4. Process smaller documents

#### Issue: Slow chat responses
**Solutions:**
1. Reduce number of retrieved chunks (k parameter)
2. Use faster embedding model
3. Optimize FAISS index settings
4. Check network latency to Azure OpenAI

### 6.4 Memory Issues

#### Issue: Out of memory errors
**Solutions:**
1. Increase system RAM
2. Reduce chunk size and overlap
3. Process documents individually
4. Use swap space (Linux)

```bash
# Add swap space (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 7. Production Deployment

### 7.1 Production Configuration

Create a production `.env` file:
```env
# Production Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Security
CORS_ORIGINS=["https://yourdomain.com"]

# Performance
WORKERS=4
MAX_FILE_SIZE=52428800  # 50MB

# Azure OpenAI (Production)
AZURE_OPENAI_API_KEY=your_production_api_key
AZURE_OPENAI_ENDPOINT=https://your-prod-resource.openai.azure.com/
```

### 7.2 Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 2 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### 7.3 Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads vector_store logs

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
# Build Docker image
docker build -t doc-chat-agent .

# Run container
docker run -d \
  --name doc-chat-agent \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/vector_store:/app/vector_store \
  --env-file .env \
  doc-chat-agent
```

### 7.4 Reverse Proxy Setup (Nginx)

Create `/etc/nginx/sites-available/doc-chat-agent`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 300s;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/doc-chat-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. Maintenance & Updates

### 8.1 Regular Maintenance Tasks

#### Daily:
- Monitor application logs
- Check disk space usage
- Verify service availability

#### Weekly:
- Review uploaded documents
- Clean up old conversation history
- Update system packages

#### Monthly:
- Update Python dependencies
- Backup vector store and metadata
- Review security configurations

### 8.2 Backup Procedures

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup uploads and vector store
cp -r uploads backups/$(date +%Y%m%d)/
cp -r vector_store backups/$(date +%Y%m%d)/

# Backup configuration
cp .env backups/$(date +%Y%m%d)/

# Create compressed archive
tar -czf backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  backups/$(date +%Y%m%d)/
```

### 8.3 Update Procedures

```bash
# Backup current installation
cp -r . ../doc-chat-agent-backup

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
sudo systemctl restart doc-chat-agent  # if using systemd
# or
docker restart doc-chat-agent  # if using Docker
```

### 8.4 Monitoring and Logging

#### Log Locations:
- Application logs: `logs/app.log`
- Uvicorn logs: Console output
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

#### Monitoring Commands:
```bash
# Monitor application logs
tail -f logs/app.log

# Monitor system resources
htop
df -h
free -h

# Check service status
systemctl status doc-chat-agent
```

---

## 🎉 Congratulations!

You have successfully set up the AI Document Chat Agent! The application should now be running and ready to process documents and answer questions.

### Next Steps:
1. Upload your first document
2. Ask questions and test the chat functionality
3. Explore the API documentation at `/api/docs`
4. Configure production settings if deploying to production
5. Set up monitoring and backup procedures

### Getting Help:
- 📚 **Documentation**: See [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
- 🔍 **Code Walkthrough**: See [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md)
- 🐛 **Issues**: Create an issue in the repository
- 💬 **Discussions**: Use GitHub Discussions for questions

**Happy chatting with your documents! 🚀** 