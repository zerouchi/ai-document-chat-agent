# AI Document Chat Agent

A sophisticated AI-powered agent that enables users to upload documents and ask questions to receive intelligent answers based on the document content. Built with FastAPI, FAISS vector store, Azure OpenAI, and a modern web interface.

## 🌟 Key Features

- **📄 Multi-Format Document Support**: Upload and process PDF, DOCX, and TXT files
- **🤖 Intelligent Q&A**: Ask natural language questions and get contextual answers
- **🔍 Vector-Based Search**: FAISS-powered similarity search for precise content retrieval
- **☁️ Azure OpenAI Integration**: Leverages GPT-4 for advanced natural language understanding
- **🎨 Modern Web Interface**: Responsive design with drag-and-drop functionality
- **📊 Real-Time Analytics**: Track documents, chunks, and conversation statistics
- **💬 Conversation Management**: Maintain context across multiple chat interactions
- **🗂️ Document Management**: View, organize, and delete uploaded documents
- **🔄 Fallback Support**: Local embeddings as backup when Azure OpenAI is unavailable

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   HTML5 UI      │ │   CSS3 Styles   │ │  JavaScript     │   │
│  │  • Responsive   │ │  • Modern       │ │  • ES6+         │   │
│  │  • Accessible   │ │  • Animations   │ │  • Async/Await  │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │ HTTP/REST API
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  API Endpoints  │ │   Middleware    │ │   Validation    │   │
│  │  • RESTful      │ │  • CORS         │ │  • Pydantic     │   │
│  │  • OpenAPI      │ │  • Security     │ │  • Type Safety  │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Document        │ │ Vector Store    │ │ Chat Service    │   │
│  │ Processor       │ │ Service         │ │                 │   │
│  │ • Text Extract  │ │ • FAISS Index   │ │ • Azure OpenAI  │   │
│  │ • Chunking      │ │ • Embeddings    │ │ • Context Mgmt  │   │
│  │ • Metadata      │ │ • Similarity    │ │ • Conversation  │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ File System     │ │ FAISS Vector    │ │ Azure OpenAI    │   │
│  │ • Documents     │ │ • Embeddings    │ │ • GPT-4 Model   │   │
│  │ • Metadata      │ │ • Index Files   │ │ • Embeddings    │   │
│  │ • Logs          │ │ • Local Backup  │ │ • Chat API      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **🔧 FastAPI Application** (`app/main.py`)
   - ASGI web framework with automatic API documentation
   - CORS middleware for cross-origin requests
   - Static file serving and template rendering

2. **📝 Document Processor** (`app/services/document_processor.py`)
   - Multi-format text extraction (PDF, DOCX, TXT)
   - Intelligent text chunking with LangChain
   - Document metadata management and lifecycle

3. **🔍 Vector Store** (`app/services/vector_store.py`)
   - FAISS-based vector database for embeddings
   - Dual embedding support (Azure OpenAI + Local fallback)
   - Efficient similarity search and document retrieval

4. **💬 Chat Service** (`app/services/chat_service.py`)
   - Azure OpenAI GPT-4 integration
   - Context-aware conversation management
   - Source citation and response formatting

5. **🌐 API Layer** (`app/api/endpoints.py`)
   - RESTful endpoints with OpenAPI documentation
   - Request/response validation with Pydantic
   - Comprehensive error handling

6. **🎨 Frontend Interface** (`templates/`, `static/`)
   - Modern, responsive web design
   - Real-time file upload with progress tracking
   - Interactive chat interface with typing indicators

## 📋 Prerequisites

- **Python 3.8+** (Recommended: Python 3.11)
- **Azure OpenAI Account** with API access (optional - local embeddings available as fallback)
- **Virtual Environment** (strongly recommended)
- **Git** for version control

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Doc_chat_ai_agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required Configuration:**
```env
# Azure OpenAI Configuration (Optional - local embeddings available as fallback)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_MODEL_NAME=gpt-4

# Application Configuration
UPLOAD_DIR=uploads
VECTOR_STORE_DIR=vector_store
MAX_FILE_SIZE=10485760  # 10MB

# Performance Configuration
TOKENIZERS_PARALLELISM=false
```

### 3. Run the Application

```bash
# Development mode (with auto-reload)
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **🌐 Main Interface**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/api/docs
- **📖 Alternative API Docs**: http://localhost:8000/api/redoc

## 📖 Usage Guide

### Document Upload

1. **Drag & Drop**: Simply drag files onto the upload area
2. **Browse Files**: Click the upload area to open file browser
3. **Supported Formats**: PDF, DOCX, TXT files up to 10MB
4. **Processing**: Watch real-time progress as documents are processed

### Asking Questions

1. **Type Questions**: Use natural language in the chat input
2. **Get Answers**: Receive AI-generated responses with source citations
3. **Follow-up**: Continue conversations with context awareness
4. **View Sources**: See which documents and sections were referenced

### Document Management

1. **View Documents**: Browse uploaded files in the sidebar
2. **Check Status**: Monitor processing status and file details
3. **Delete Files**: Remove documents when no longer needed
4. **Statistics**: Track system usage and performance metrics

## 🔧 API Reference

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload a new document |
| `GET` | `/api/v1/documents` | List all uploaded documents |
| `GET` | `/api/v1/documents/{id}` | Get specific document details |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Send a chat message |
| `GET` | `/api/v1/conversations/{id}/history` | Get conversation history |
| `DELETE` | `/api/v1/conversations/{id}` | Clear conversation |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/stats` | Get system statistics |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/search` | Direct document search |

## 🏗️ Project Structure

```
Doc_chat_ai_agent/
├── 📁 app/                          # Main application package
│   ├── 📄 main.py                   # FastAPI application entry point
│   ├── 📁 core/                     # Core configuration and utilities
│   │   ├── 📄 config.py             # Environment and app configuration
│   │   └── 📄 __init__.py
│   ├── 📁 models/                   # Data models and schemas
│   │   ├── 📄 schemas.py            # Pydantic request/response models
│   │   └── 📄 __init__.py
│   ├── 📁 services/                 # Business logic services
│   │   ├── 📄 document_processor.py # Document processing and management
│   │   ├── 📄 vector_store.py       # Vector database operations
│   │   ├── 📄 chat_service.py       # AI chat and conversation handling
│   │   ├── 📄 local_embeddings.py   # Local embedding fallback
│   │   ├── 📄 local_chat.py         # Local chat fallback
│   │   └── 📄 __init__.py
│   ├── 📁 api/                      # API layer
│   │   ├── 📄 endpoints.py          # REST API endpoint definitions
│   │   └── 📄 __init__.py
│   └── 📄 __init__.py
├── 📁 static/                       # Frontend static assets
│   ├── 📁 css/
│   │   └── 📄 style.css             # Application styles
│   └── 📁 js/
│       └── 📄 app.js                # Frontend JavaScript logic
├── 📁 templates/                    # HTML templates
│   └── 📄 index.html                # Main application template
├── 📁 uploads/                      # Document storage directory
├── 📁 vector_store/                 # FAISS index storage
├── 📁 logs/                         # Application logs
├── 📄 requirements.txt              # Python dependencies
├── 📄 env.example                   # Environment variables template
├── 📄 run.py                        # Application startup script
├── 📄 README.md                     # This documentation
├── 📄 ARCHITECTURE.md               # Detailed architecture documentation
└── 📄 CODE_WALKTHROUGH.md           # Step-by-step code explanation
```

## 🔒 Security & Best Practices

### Environment Security
- ✅ Environment variables for sensitive configuration
- ✅ API key protection and validation
- ✅ File type and size validation
- ✅ Input sanitization and validation

### Production Considerations
- 🔧 Configure specific CORS origins
- 🔧 Set up proper logging and monitoring
- 🔧 Use production WSGI server (Gunicorn)
- 🔧 Configure SSL/TLS certificates
- 🔧 Set up rate limiting and authentication

## 🚀 Deployment Options

### Local Development
```bash
python run.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing & Validation

### Manual Testing Checklist
- [ ] Upload various document formats (PDF, DOCX, TXT)
- [ ] Test chat functionality with different question types
- [ ] Verify document management features
- [ ] Check error handling with invalid inputs
- [ ] Test conversation context and history
- [ ] Validate source citations and accuracy

### API Testing
Use the interactive documentation at `/api/docs` to test all endpoints directly.

## 🔧 Troubleshooting

### Common Issues

**🔴 Azure OpenAI Connection Errors**
- Verify API key and endpoint in `.env` file
- Check Azure OpenAI service availability and quotas
- Ensure correct deployment name and model version

**🔴 File Upload Issues**
- Check file size limits (default: 10MB)
- Verify supported file formats (PDF, DOCX, TXT)
- Ensure upload directory permissions

**🔴 Vector Store Errors**
- Verify FAISS installation: `pip install faiss-cpu`
- Check vector store directory permissions
- Monitor memory usage for large document collections

**🔴 Local Embeddings Issues**
- Ensure sentence-transformers is installed
- Check available disk space for model downloads
- Verify internet connection for initial model download

### Performance Optimization

**📈 For Large Document Collections:**
- Increase chunk size for better context
- Use more powerful embedding models
- Consider distributed vector storage

**📈 For High Traffic:**
- Implement caching strategies
- Use connection pooling
- Set up load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **FAISS** - Efficient similarity search and clustering library
- **Azure OpenAI** - Powerful language models and embeddings
- **LangChain** - Framework for developing LLM applications
- **Sentence Transformers** - State-of-the-art sentence embeddings

## 📞 Support & Documentation

- 📚 **Detailed Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- 🔍 **Code Walkthrough**: See [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md)
- 🐛 **Issues**: Create an issue in the repository
- 💬 **Discussions**: Use GitHub Discussions for questions

---

**🚀 Built with ❤️ using FastAPI, FAISS, and Azure OpenAI**

*Ready to transform your document interactions with AI? Get started in minutes!* 