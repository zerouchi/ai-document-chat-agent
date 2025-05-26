"""
Local chat service that provides basic responses using document context.
Works without external LLM APIs.
"""

import uuid
from typing import List, Dict, Any, Optional
from app.services.vector_store import VectorStore


class LocalChatService:
    """Local chat service that provides responses based on document context."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        # Store conversation history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def _format_sources(self, context_chunks: List[Dict[str, Any]]) -> List[str]:
        """Format source information from context chunks."""
        sources = []
        seen_docs = set()
        
        for chunk in context_chunks:
            doc_info = f"{chunk['filename']} (chunk {chunk['chunk_index'] + 1})"
            if doc_info not in seen_docs:
                sources.append(doc_info)
                seen_docs.add(doc_info)
        
        return sources
    
    def _create_simple_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Create a simple response based on the context chunks."""
        if not context_chunks:
            return f"I couldn't find any relevant information about '{question}' in the uploaded documents. Please make sure you've uploaded documents that contain information related to your question."
        
        # Extract the most relevant text snippets
        relevant_texts = []
        for chunk in context_chunks[:3]:  # Use top 3 most relevant chunks
            text = chunk['text'].strip()
            if len(text) > 200:
                # Truncate long texts but try to keep complete sentences
                sentences = text.split('. ')
                truncated = '. '.join(sentences[:2])
                if len(truncated) < 150 and len(sentences) > 2:
                    truncated = '. '.join(sentences[:3])
                text = truncated + '...' if len(truncated) < len(chunk['text']) else truncated
            relevant_texts.append(text)
        
        # Create a simple response
        response_parts = [
            f"Based on the uploaded documents, here's what I found regarding '{question}':",
            "",
        ]
        
        for i, text in enumerate(relevant_texts, 1):
            response_parts.append(f"{i}. {text}")
            response_parts.append("")
        
        response_parts.append("This information was extracted from the uploaded documents. For more detailed analysis, consider configuring an AI language model.")
        
        return "\n".join(response_parts)
    
    def chat(self, question: str, conversation_id: Optional[str] = None, k: int = 5) -> Dict[str, Any]:
        """Process a chat question and return a response with sources."""
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Retrieve relevant context from vector store
            context_chunks = self.vector_store.similarity_search(question, k=k)
            
            # Create simple response
            answer = self._create_simple_response(question, context_chunks)
            
            # Format sources
            sources = self._format_sources(context_chunks)
            
            # Store conversation history
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            self.conversations[conversation_id].extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])
            
            # Keep only last 10 exchanges per conversation
            if len(self.conversations[conversation_id]) > 20:
                self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
            
            return {
                "answer": answer,
                "sources": sources,
                "conversation_id": conversation_id,
                "context_chunks_found": len(context_chunks),
                "chat_type": "local"
            }
            
        except Exception as e:
            error_msg = f"Error processing chat request: {str(e)}"
            print(error_msg)
            
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again or check if you have uploaded any documents.",
                "sources": [],
                "conversation_id": conversation_id,
                "error": error_msg,
                "chat_type": "local"
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a given conversation ID."""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history for a given conversation ID."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def get_active_conversations(self) -> List[str]:
        """Get list of active conversation IDs."""
        return list(self.conversations.keys())
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Get chat service statistics."""
        total_messages = sum(len(conv) for conv in self.conversations.values())
        
        return {
            "active_conversations": len(self.conversations),
            "total_messages": total_messages,
            "vector_store_stats": self.vector_store.get_stats(),
            "chat_type": "local"
        } 