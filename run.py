#!/usr/bin/env python3
"""
Startup script for the AI Document Chat Agent.
"""

import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting AI Document Chat Agent...")
    print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/api/docs")
    print("🔧 Make sure to configure your .env file with Azure OpenAI credentials")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 