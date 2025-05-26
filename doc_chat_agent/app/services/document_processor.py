"""
Document processing service for handling file uploads and text extraction.
"""

import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings


class DocumentProcessor:
    """Service for processing and managing documents."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        self.metadata_file = os.path.join(settings.upload_dir, "metadata.json")
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load document metadata from file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """Save document metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise ValueError(f"Error extracting text from TXT: {str(e)}")
        return text
    
    def extract_text(self, file_path: str, file_extension: str) -> str:
        """Extract text from file based on extension."""
        if file_extension.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension.lower() == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension.lower() == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process uploaded document and extract text chunks."""
        document_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        
        try:
            # Extract text from document
            text = self.extract_text(file_path, file_extension)
            
            if not text.strip():
                raise ValueError("No text content found in the document")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Store metadata
            file_size = os.path.getsize(file_path)
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "file_path": file_path,
                "file_size": file_size,
                "upload_date": datetime.now().isoformat(),
                "status": "processed",
                "chunks_count": len(chunks),
                "file_extension": file_extension
            }
            
            self.metadata[document_id] = metadata
            self._save_metadata()
            
            return {
                "document_id": document_id,
                "chunks": chunks,
                "metadata": metadata
            }
            
        except Exception as e:
            # Update metadata with error status
            if document_id in self.metadata:
                self.metadata[document_id]["status"] = "error"
                self.metadata[document_id]["error"] = str(e)
                self._save_metadata()
            raise e
    
    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get document information by ID."""
        if document_id not in self.metadata:
            raise ValueError(f"Document with ID {document_id} not found")
        return self.metadata[document_id]
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all processed documents."""
        return list(self.metadata.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document and its metadata."""
        if document_id not in self.metadata:
            return False
        
        # Remove file if it exists
        file_path = self.metadata[document_id].get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove metadata
        del self.metadata[document_id]
        self._save_metadata()
        
        return True 