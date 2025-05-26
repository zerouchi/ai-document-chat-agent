"""
FastAPI endpoints for document upload, chat, and management operations.
"""

import os
import shutil
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ChatRequest, ChatResponse, DocumentUploadResponse, 
    DocumentListResponse, DocumentInfo, ErrorResponse
)
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.chat_service import ChatService
from app.services.local_chat import LocalChatService
from app.core.config import settings

# Initialize services lazily
document_processor = None
vector_store = None
chat_service = None

def get_services():
    """Get or initialize services."""
    global document_processor, vector_store, chat_service
    
    if document_processor is None:
        document_processor = DocumentProcessor()
    
    if vector_store is None:
        vector_store = VectorStore()
    
    if chat_service is None:
        # Try to use Azure OpenAI chat service first, fallback to local chat
        try:
            # Check if Azure OpenAI is properly configured
            if (settings.azure_openai_api_key and 
                settings.azure_openai_endpoint and 
                settings.azure_openai_deployment_name ):
                chat_service = ChatService(vector_store)
                print("✅ Using Azure OpenAI chat service")
            else:
                chat_service = LocalChatService(vector_store)
                print("✅ Using local chat service (no Azure OpenAI configured)")
        except Exception as e:
            print(f"⚠️  Failed to initialize Azure OpenAI chat service: {e}")
            print("🔄 Falling back to local chat service...")
            chat_service = LocalChatService(vector_store)
    
    return document_processor, vector_store, chat_service

# Create router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    
    # Get services
    doc_processor, vec_store, _ = get_services()
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (if available)
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {settings.max_file_size} bytes"
        )
    
    file_path = None
    try:
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        result = doc_processor.process_document(file_path, file.filename)
        
        # Add to vector store (only if Azure OpenAI is configured)
        try:
            vec_store.add_documents(
                chunks=result["chunks"],
                document_id=result["document_id"],
                filename=file.filename
            )
            message = "Document uploaded and processed successfully"
        except ValueError as ve:
            if "No embedding service available" in str(ve):
                message = "Document uploaded and processed successfully (Note: Vector search disabled - no embedding service available)"
            else:
                raise ve
        
        return DocumentUploadResponse(
            message=message,
            filename=file.filename,
            file_size=file.size or os.path.getsize(file_path),
            document_id=result["document_id"]
        )
        
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error processing upload for file {file.filename}: {str(e)}", exc_info=True)
        
        # Clean up file if processing failed
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file {file_path}: {cleanup_error}")
        
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI agent using uploaded documents as context."""
    
    # Get services
    _, _, chat_svc = get_services()
    
    try:
        result = chat_svc.chat(
            question=request.question,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=result["conversation_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    
    # Get services
    doc_processor, _, _ = get_services()
    
    try:
        documents = doc_processor.list_documents()
        
        document_infos = [
            DocumentInfo(
                document_id=doc["document_id"],
                filename=doc["filename"],
                file_size=doc["file_size"],
                upload_date=doc["upload_date"],
                status=doc["status"]
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_infos,
            total_count=len(document_infos)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and remove it from the vector store."""
    
    # Get services
    doc_processor, vec_store, _ = get_services()
    
    try:
        # Remove from vector store
        vector_removed = vec_store.remove_document(document_id)
        
        # Remove from document processor
        doc_removed = doc_processor.delete_document(document_id)
        
        if not doc_removed:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document_info(document_id: str):
    """Get information about a specific document."""
    
    # Get services
    doc_processor, _, _ = get_services()
    
    try:
        doc_info = doc_processor.get_document_info(document_id)
        
        return DocumentInfo(
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            file_size=doc_info["file_size"],
            upload_date=doc_info["upload_date"],
            status=doc_info["status"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get system statistics."""
    
    # Get services
    doc_processor, _, chat_svc = get_services()
    
    try:
        chat_stats = chat_svc.get_chat_stats()
        documents = doc_processor.list_documents()
        
        return {
            "documents": {
                "total_count": len(documents),
                "processed_count": len([d for d in documents if d["status"] == "processed"]),
                "error_count": len([d for d in documents if d["status"] == "error"])
            },
            "chat": {
                "active_conversations": chat_stats["active_conversations"],
                "total_messages": chat_stats["total_messages"]
            },
            "vector_store": chat_stats["vector_store_stats"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    
    # Get services
    _, _, chat_svc = get_services()
    
    try:
        history = chat_svc.get_conversation_history(conversation_id)
        return {"conversation_id": conversation_id, "history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history for a specific conversation."""
    
    # Get services
    _, _, chat_svc = get_services()
    
    try:
        cleared = chat_svc.clear_conversation(conversation_id)
        
        if not cleared:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation cleared successfully", "conversation_id": conversation_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_documents(query: str, k: int = 5):
    """Search for relevant document chunks."""
    
    # Get services
    _, vec_store, _ = get_services()
    
    try:
        results = vec_store.similarity_search(query, k=k)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 