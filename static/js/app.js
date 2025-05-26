// AI Document Chat Agent - JavaScript Application

class DocumentChatApp {
    constructor() {
        this.conversationId = null;
        this.apiBase = '/api/v1';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDocuments();
        this.loadStats();
        this.setupCharacterCounter();
    }

    setupEventListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Chat
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.addEventListener('input', this.updateSendButton.bind(this));
        sendBtn.addEventListener('click', this.sendMessage.bind(this));

        // Other buttons
        document.getElementById('refreshDocsBtn').addEventListener('click', this.loadDocuments.bind(this));
        document.getElementById('clearChatBtn').addEventListener('click', this.clearChat.bind(this));
    }

    setupCharacterCounter() {
        const chatInput = document.getElementById('chatInput');
        const charCount = document.getElementById('charCount');

        chatInput.addEventListener('input', () => {
            const count = chatInput.value.length;
            charCount.textContent = `${count}/1000`;
            
            if (count > 900) {
                charCount.style.color = '#f56565';
            } else if (count > 800) {
                charCount.style.color = '#ed8936';
            } else {
                charCount.style.color = '#a0aec0';
            }
        });
    }

    // File Upload Handlers
    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        const validFiles = files.filter(file => {
            const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
            const validExtensions = ['.pdf', '.docx', '.txt'];
            const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
            
            return validTypes.includes(file.type) || validExtensions.includes(extension);
        });

        if (validFiles.length === 0) {
            this.showToast('Please select valid files (PDF, DOCX, TXT)', 'error');
            return;
        }

        for (const file of validFiles) {
            await this.uploadSingleFile(file);
        }

        // Reset file input
        document.getElementById('fileInput').value = '';
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const progressContainer = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        try {
            progressContainer.style.display = 'block';
            progressFill.style.width = '0%';
            progressText.textContent = '0%';

            // Simulate progress for better UX
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 30;
                if (progress > 90) progress = 90;
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `${Math.round(progress)}%`;
            }, 200);

            const response = await fetch(`${this.apiBase}/upload`, {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = '100%';

            if (response.ok) {
                const result = await response.json();
                this.showToast(`Successfully uploaded: ${result.filename}`, 'success');
                this.loadDocuments();
                this.loadStats();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

        } catch (error) {
            this.showToast(`Upload failed: ${error.message}`, 'error');
        } finally {
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 1000);
        }
    }

    // Chat Functions
    updateSendButton() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        
        sendBtn.disabled = chatInput.value.trim().length === 0;
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();

        if (!message) return;

        // Clear input and disable send button
        chatInput.value = '';
        this.updateSendButton();
        document.getElementById('charCount').textContent = '0/1000';
        document.getElementById('charCount').style.color = '#a0aec0';

        // Add user message to chat
        this.addMessageToChat(message, 'user');

        // Show AI thinking indicator
        this.showAIThinking();

        try {
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: message,
                    conversation_id: this.conversationId
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.conversationId = result.conversation_id;
                this.addMessageToChat(result.answer, 'assistant', result.sources);
                this.loadStats();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Chat request failed');
            }

        } catch (error) {
            this.addMessageToChat(`Sorry, I encountered an error: ${error.message}`, 'assistant');
            this.showToast('Failed to get response', 'error');
        } finally {
            this.hideAIThinking();
        }
    }

    addMessageToChat(content, sender, sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        
        // Remove welcome message if it exists
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        // Add sources for assistant messages
        if (sender === 'assistant' && sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
            
            sources.forEach(source => {
                const sourceSpan = document.createElement('span');
                sourceSpan.className = 'source-item';
                sourceSpan.textContent = source;
                sourcesDiv.appendChild(sourceSpan);
            });
            
            messageContent.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-robot"></i>
                <h3>Welcome to AI Document Chat Agent!</h3>
                <p>Upload some documents and start asking questions. I'll help you find answers based on your uploaded content.</p>
            </div>
        `;
        this.conversationId = null;
        this.showToast('Chat cleared', 'success');
    }

    // Document Management
    async loadDocuments() {
        try {
            const response = await fetch(`${this.apiBase}/documents`);
            if (response.ok) {
                const result = await response.json();
                this.displayDocuments(result.documents);
            } else {
                throw new Error('Failed to load documents');
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showToast('Failed to load documents', 'error');
        }
    }

    displayDocuments(documents) {
        const documentsList = document.getElementById('documentsList');
        
        if (documents.length === 0) {
            documentsList.innerHTML = '<p class="no-documents">No documents uploaded yet</p>';
            return;
        }

        documentsList.innerHTML = documents.map(doc => `
            <div class="document-item">
                <div class="document-info">
                    <div class="document-name">${doc.filename}</div>
                    <div class="document-meta">
                        ${this.formatFileSize(doc.file_size)} • ${this.formatDate(doc.upload_date)}
                        <span class="status-${doc.status}">${doc.status}</span>
                    </div>
                </div>
                <div class="document-actions">
                    <button class="btn btn-danger btn-small" onclick="app.deleteDocument('${doc.document_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Document deleted successfully', 'success');
                this.loadDocuments();
                this.loadStats();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Delete failed');
            }
        } catch (error) {
            this.showToast(`Failed to delete document: ${error.message}`, 'error');
        }
    }

    // Statistics
    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStats(stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateStats(stats) {
        document.getElementById('totalDocs').textContent = stats.documents.total_count;
        document.getElementById('totalChunks').textContent = stats.vector_store.total_chunks;
        document.getElementById('totalConversations').textContent = stats.chat.active_conversations;
    }

    // Utility Functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showAIThinking() {
        const chatMessages = document.getElementById('chatMessages');
        
        // Create thinking indicator
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message message-assistant thinking-indicator';
        thinkingDiv.id = 'aiThinking';
        
        thinkingDiv.innerHTML = `
            <div class="message-content thinking-content">
                <div class="thinking-animation">
                    <div class="thinking-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="thinking-text">AI is thinking...</span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(thinkingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideAIThinking() {
        const thinkingIndicator = document.getElementById('aiThinking');
        if (thinkingIndicator) {
            thinkingIndicator.remove();
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);

        // Remove on click
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentChatApp();
});

// Handle page visibility change to refresh stats
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.app) {
        window.app.loadStats();
    }
}); 