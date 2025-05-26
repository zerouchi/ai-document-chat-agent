"""
Chat service that integrates Azure OpenAI for question answering using retrieved document context.
"""

import uuid
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI

from app.core.config import settings
from app.services.vector_store import VectorStore
import os
import traceback

class ChatService:
    """Service for handling chat interactions with document context."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
        # Initialize LLM only if Azure OpenAI is properly configured
        if (settings.azure_openai_api_key and 
            settings.azure_openai_endpoint and 
            settings.azure_openai_deployment_name):
            try:
                self.llm = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_version=settings.azure_openai_api_version
                )
                print(self.llm)
                # Test the connection
                try:
                    test_response = self.llm.chat.completions.create(
                        model=settings.azure_openai_deployment_name,
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5,
                        timeout=10
                    )
                    print("✅ Azure OpenAI chat service configured and tested successfully")
                except Exception as e:
                    print(f"⚠️  Azure OpenAI test connection failed: {e}")
                    print("🔄 Will proceed without test - connection will be verified during actual use")
                    # Don't set self.llm = None here, let it try during actual chat
            except Exception as e:
                print(f"⚠️  Azure OpenAI chat connection failed: {e}")
                self.llm = None
        else:
            self.llm = None
            print("⚠️  Azure OpenAI not configured. Chat service will work in limited mode.")
        # Store conversation history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def _create_system_prompt(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Create system prompt with document context."""
        if not context_chunks:
            return """You are a helpful AI assistant. The user is asking a question, but no relevant documents were found in the knowledge base. Please let them know that you don't have specific information about their query in the uploaded documents, but you can provide general assistance if helpful."""
        
        context_text = "\n\n".join([
            f"Document: {chunk['filename']}\nContent: {chunk['text']}"
            for chunk in context_chunks
        ])
        
        return f"""You are a helpful AI assistant that answers questions based on the provided document context. 

CONTEXT FROM UPLOADED DOCUMENTS:
{context_text}

INSTRUCTIONS:
1. Answer the user's question using ONLY the information provided in the context above
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Always cite which document(s) you're referencing in your answer
4. Be concise but comprehensive
5. If asked about something not in the documents, explain that the information is not available in the uploaded documents

Remember: Only use information from the provided context. Do not make up information or use knowledge outside of the provided documents."""
    
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
    
    def chat(self, question: str, conversation_id: Optional[str] = None, k: int = 5) -> Dict[str, Any]:
        """Process a chat question and return an answer with sources."""
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Check if LLM is configured
        if not self.llm:
            return {
                "answer": "I apologize, but the AI chat service is not configured. Please set up your Azure OpenAI credentials in the .env file to enable chat functionality.",
                "sources": [],
                "conversation_id": conversation_id,
                "error": "Azure OpenAI not configured"
            }
        
        try:
            # Retrieve relevant context from vector store
            context_chunks = self.vector_store.similarity_search(question, k=k)
            
            # Create system prompt with context
            system_prompt = self._create_system_prompt(context_chunks)
            
            # Prepare messages for OpenAI API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            # Add conversation history if available
            if conversation_id in self.conversations:
                # Add recent conversation history (last 3 exchanges)
                recent_history = self.conversations[conversation_id][-6:]  # 3 Q&A pairs
                history_messages = []
                for entry in recent_history:
                    if entry["role"] == "user":
                        history_messages.append({"role": "user", "content": entry["content"]})
                    elif entry["role"] == "assistant":
                        history_messages.append({"role": "assistant", "content": entry["content"]})
                
                # Insert history before the current question
                messages = [messages[0]] + history_messages + [messages[1]]
            
            # Get response from Azure OpenAI
            try:
                print(f"🔄 Sending request to Azure OpenAI with {len(messages)} messages...")
                response = self.llm.chat.completions.create(
                    model=settings.azure_openai_deployment_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=30
                )
                answer = response.choices[0].message.content
                print(f"✅ Received response from Azure OpenAI: {len(answer)} characters")
            except Exception as e:
                error_msg = f"Failed to get response from Azure OpenAI: {str(e)}"
                print(f"❌ Azure OpenAI Error: {error_msg}")
                print(f"   Model: {settings.azure_openai_deployment_name}")
                print(f"   Endpoint: {settings.azure_openai_endpoint}")
                print(f"   Messages count: {len(messages)}")
                return {
                    "answer": "I apologize, but there was an error retrieving the response from the AI service. Please try again later.",
                    "sources": [],
                    "conversation_id": conversation_id,
                    "error": error_msg
                }
            
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
                "context_chunks_found": len(context_chunks)
            }
            
        except Exception as e:
            error_msg = f"Error processing chat request: {str(e)} {traceback.format_exc()}"
            print(error_msg)
            
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again or contact support if the issue persists.",
                "sources": [],
                "conversation_id": conversation_id,
                "error": error_msg
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
            "vector_store_stats": self.vector_store.get_stats()
        } 