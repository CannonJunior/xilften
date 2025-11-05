/**
 * AI Interface Module
 *
 * Handles all AI-powered features including:
 * - Content mashup generation (streaming)
 * - High-concept story pitches
 * - Personalized recommendations
 * - Similar title discovery
 * - General media chat (streaming)
 *
 * Uses Server-Sent Events (SSE) for streaming responses
 */

import { API } from './api-client.js';

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

class AIInterfaceState {
    constructor() {
        this.conversationHistory = [];
        this.currentStream = null;
        this.isStreaming = false;
    }

    addMessage(role, content) {
        this.conversationHistory.push({ role, content });
    }

    clearHistory() {
        this.conversationHistory = [];
    }

    cancelStream() {
        if (this.currentStream) {
            this.currentStream.close();
            this.currentStream = null;
            this.isStreaming = false;
        }
    }
}

const state = new AIInterfaceState();

// ============================================================================
// STREAMING UTILITIES
// ============================================================================

/**
 * Handle Server-Sent Events (SSE) stream
 * @param {string} url - Streaming endpoint URL
 * @param {Object} data - Request payload
 * @param {Function} onChunk - Callback for each chunk
 * @param {Function} onComplete - Callback when complete
 * @param {Function} onError - Callback on error
 */
async function handleStreamingResponse(url, data, onChunk, onComplete, onError) {
    state.isStreaming = true;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (state.isStreaming) {
            const { done, value } = await reader.read();

            if (done) break;

            // Decode chunk
            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const chunk = line.slice(6); // Remove 'data: ' prefix
                    if (chunk.trim()) {
                        onChunk(chunk);
                    }
                }
            }
        }

        state.isStreaming = false;
        if (onComplete) onComplete();

    } catch (error) {
        state.isStreaming = false;
        console.error('Streaming error:', error);
        if (onError) onError(error);
    }
}

// ============================================================================
// CONTENT MASHUP
// ============================================================================

export class MashupGenerator {
    /**
     * Generate a content mashup (non-streaming)
     * @param {string} userQuery - User's mashup request
     * @param {Array} references - Array of {title, media_type, aspects}
     * @param {string} detailLevel - 'simple' or 'detailed'
     * @param {number} temperature - Creativity (0.0-2.0)
     * @returns {Promise<Object>} Mashup result
     */
    static async generate(userQuery, references, detailLevel = 'simple', temperature = 0.8) {
        const response = await API.post('/api/ai/mashup', {
            user_query: userQuery,
            references: references,
            detail_level: detailLevel,
            temperature: temperature
        });

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Mashup generation failed');
        }
    }

    /**
     * Generate a content mashup with streaming
     * @param {string} userQuery - User's mashup request
     * @param {Array} references - Array of {title, media_type, aspects}
     * @param {Function} onChunk - Callback for each chunk
     * @param {Function} onComplete - Callback when complete
     * @param {Function} onError - Callback on error
     * @param {string} detailLevel - 'simple' or 'detailed'
     * @param {number} temperature - Creativity (0.0-2.0)
     */
    static async generateStream(
        userQuery,
        references,
        onChunk,
        onComplete,
        onError,
        detailLevel = 'simple',
        temperature = 0.8
    ) {
        await handleStreamingResponse(
            '/api/ai/mashup/stream',
            {
                user_query: userQuery,
                references: references,
                detail_level: detailLevel,
                temperature: temperature
            },
            onChunk,
            onComplete,
            onError
        );
    }

    /**
     * Cancel ongoing streaming generation
     */
    static cancel() {
        state.cancelStream();
    }
}

// ============================================================================
// HIGH-CONCEPT PITCHES
// ============================================================================

export class HighConceptGenerator {
    /**
     * Generate a high-concept story pitch
     * @param {Array} references - Array of {title, media_type, aspects}
     * @param {string} extractionFocus - What to extract (e.g., "witty dialogue, action")
     * @param {string} pitchType - 'full' or 'logline'
     * @param {number} temperature - Creativity (0.0-2.0)
     * @returns {Promise<Object>} Pitch result
     */
    static async generate(references, extractionFocus, pitchType = 'full', temperature = 0.9) {
        const response = await API.post('/api/ai/high-concept', {
            references: references,
            extraction_focus: extractionFocus,
            pitch_type: pitchType,
            temperature: temperature
        });

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'High-concept generation failed');
        }
    }
}

// ============================================================================
// RECOMMENDATIONS
// ============================================================================

export class RecommendationEngine {
    /**
     * Get personalized recommendations
     * @param {string} userQuery - User's request/mood
     * @param {Object} userPreferences - Genre preferences, favorite directors, etc.
     * @param {Array} viewingHistory - Titles already watched
     * @param {boolean} moodBased - Focus on current mood
     * @param {number} temperature - Creativity (0.0-2.0)
     * @returns {Promise<Object>} Recommendations result
     */
    static async getRecommendations(
        userQuery,
        userPreferences = null,
        viewingHistory = null,
        moodBased = false,
        temperature = 0.7
    ) {
        const response = await API.post('/api/ai/recommend', {
            user_query: userQuery,
            user_preferences: userPreferences,
            viewing_history: viewingHistory,
            mood_based: moodBased,
            temperature: temperature
        });

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Recommendation generation failed');
        }
    }

    /**
     * Find titles similar to a reference
     * @param {string} referenceTitle - Title to find similar matches for
     * @param {Array} matchAspects - Aspects to match (tone, genre, style, etc.)
     * @param {number} count - Number of recommendations (1-20)
     * @param {number} temperature - Creativity (0.0-2.0)
     * @returns {Promise<Object>} Similar titles result
     */
    static async findSimilar(referenceTitle, matchAspects = null, count = 7, temperature = 0.6) {
        const response = await API.post('/api/ai/similar', {
            reference_title: referenceTitle,
            match_aspects: matchAspects,
            count: count,
            temperature: temperature
        });

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Similar titles search failed');
        }
    }
}

// ============================================================================
// CHAT INTERFACE
// ============================================================================

export class AIChat {
    /**
     * Send a chat message (non-streaming)
     * @param {string} userMessage - User's message
     * @param {boolean} includeHistory - Include conversation history
     * @param {number} temperature - Creativity (0.0-2.0)
     * @returns {Promise<Object>} Chat response
     */
    static async sendMessage(userMessage, includeHistory = true, temperature = 0.7) {
        const conversationHistory = includeHistory ? state.conversationHistory : null;

        const response = await API.post('/api/ai/chat', {
            user_message: userMessage,
            conversation_history: conversationHistory,
            temperature: temperature
        });

        if (response.success) {
            // Update conversation history
            state.addMessage('user', userMessage);
            state.addMessage('assistant', response.data.content);

            return response.data;
        } else {
            throw new Error(response.error || 'Chat failed');
        }
    }

    /**
     * Send a chat message with streaming
     * @param {string} userMessage - User's message
     * @param {Function} onChunk - Callback for each chunk
     * @param {Function} onComplete - Callback when complete
     * @param {Function} onError - Callback on error
     * @param {boolean} includeHistory - Include conversation history
     * @param {number} temperature - Creativity (0.0-2.0)
     */
    static async sendMessageStream(
        userMessage,
        onChunk,
        onComplete,
        onError,
        includeHistory = true,
        temperature = 0.7
    ) {
        const conversationHistory = includeHistory ? state.conversationHistory : null;

        // Add user message to history
        state.addMessage('user', userMessage);

        let assistantResponse = '';

        await handleStreamingResponse(
            '/api/ai/chat/stream',
            {
                user_message: userMessage,
                conversation_history: conversationHistory,
                temperature: temperature
            },
            (chunk) => {
                assistantResponse += chunk;
                onChunk(chunk);
            },
            () => {
                // Add complete assistant response to history
                state.addMessage('assistant', assistantResponse);
                if (onComplete) onComplete();
            },
            onError
        );
    }

    /**
     * Clear conversation history
     */
    static clearHistory() {
        state.clearHistory();
    }

    /**
     * Get conversation history
     * @returns {Array} Conversation history
     */
    static getHistory() {
        return state.conversationHistory;
    }

    /**
     * Cancel ongoing streaming chat
     */
    static cancel() {
        state.cancelStream();
    }
}

// ============================================================================
// STATUS AND UTILITIES
// ============================================================================

export class AIService {
    /**
     * Check AI service status
     * @returns {Promise<Object>} Service status and capabilities
     */
    static async getStatus() {
        const response = await API.get('/api/ai/status');

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Status check failed');
        }
    }

    /**
     * List available prompt templates
     * @returns {Promise<Object>} Template list
     */
    static async listTemplates() {
        const response = await API.get('/api/ai/templates');

        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Template listing failed');
        }
    }

    /**
     * Check if currently streaming
     * @returns {boolean} True if streaming
     */
    static isStreaming() {
        return state.isStreaming;
    }

    /**
     * Cancel any ongoing streaming operation
     */
    static cancelStream() {
        state.cancelStream();
    }
}

// ============================================================================
// UI HELPER FUNCTIONS
// ============================================================================

/**
 * Create a chat interface in a container
 * @param {HTMLElement} container - Container element
 * @param {Object} options - Configuration options
 */
export function createChatInterface(container, options = {}) {
    const {
        placeholder = 'Ask about movies, TV shows, anime...',
        showHistory = true,
        enableStreaming = true,
        onResponse = null
    } = options;

    // Create HTML structure
    container.innerHTML = `
        <div class="ai-chat-interface">
            ${showHistory ? '<div class="chat-history" id="chat-history"></div>' : ''}
            <div class="chat-input-container">
                <textarea
                    id="chat-input"
                    class="chat-input"
                    placeholder="${placeholder}"
                    rows="3"
                ></textarea>
                <div class="chat-actions">
                    <button id="chat-send-btn" class="btn btn-primary">
                        ${enableStreaming ? 'Stream' : 'Send'}
                    </button>
                    <button id="chat-cancel-btn" class="btn btn-secondary" style="display:none;">
                        Cancel
                    </button>
                    ${showHistory ? '<button id="chat-clear-btn" class="btn btn-secondary">Clear History</button>' : ''}
                </div>
            </div>
            <div class="chat-response" id="chat-response"></div>
        </div>
    `;

    const input = container.querySelector('#chat-input');
    const sendBtn = container.querySelector('#chat-send-btn');
    const cancelBtn = container.querySelector('#chat-cancel-btn');
    const clearBtn = container.querySelector('#chat-clear-btn');
    const responseDiv = container.querySelector('#chat-response');
    const historyDiv = container.querySelector('#chat-history');

    // Send message handler
    const sendMessage = async () => {
        const message = input.value.trim();
        if (!message) return;

        // Disable input
        input.disabled = true;
        sendBtn.style.display = 'none';
        cancelBtn.style.display = 'inline-block';

        // Clear response
        responseDiv.textContent = '';
        responseDiv.classList.add('streaming');

        try {
            if (enableStreaming) {
                // Streaming mode
                await AIChat.sendMessageStream(
                    message,
                    (chunk) => {
                        responseDiv.textContent += chunk;
                        responseDiv.scrollTop = responseDiv.scrollHeight;
                    },
                    () => {
                        // Complete
                        input.disabled = false;
                        input.value = '';
                        sendBtn.style.display = 'inline-block';
                        cancelBtn.style.display = 'none';
                        responseDiv.classList.remove('streaming');

                        if (onResponse) onResponse(responseDiv.textContent);
                        if (showHistory) updateChatHistory();
                    },
                    (error) => {
                        // Error
                        responseDiv.textContent = `Error: ${error.message}`;
                        responseDiv.classList.add('error');
                        input.disabled = false;
                        sendBtn.style.display = 'inline-block';
                        cancelBtn.style.display = 'none';
                    }
                );
            } else {
                // Non-streaming mode
                const result = await AIChat.sendMessage(message);
                responseDiv.textContent = result.content;
                input.disabled = false;
                input.value = '';
                sendBtn.style.display = 'inline-block';
                responseDiv.classList.remove('streaming');

                if (onResponse) onResponse(result.content);
                if (showHistory) updateChatHistory();
            }
        } catch (error) {
            responseDiv.textContent = `Error: ${error.message}`;
            responseDiv.classList.add('error');
            input.disabled = false;
            sendBtn.style.display = 'inline-block';
            cancelBtn.style.display = 'none';
        }
    };

    // Update chat history display
    const updateChatHistory = () => {
        if (!historyDiv) return;

        const history = AIChat.getHistory();
        historyDiv.innerHTML = history.map(msg => `
            <div class="chat-message chat-message-${msg.role}">
                <div class="chat-message-role">${msg.role === 'user' ? 'You' : 'AI'}</div>
                <div class="chat-message-content">${msg.content}</div>
            </div>
        `).join('');

        historyDiv.scrollTop = historyDiv.scrollHeight;
    };

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            AIChat.cancel();
            input.disabled = false;
            sendBtn.style.display = 'inline-block';
            cancelBtn.style.display = 'none';
            responseDiv.classList.remove('streaming');
            responseDiv.textContent += '\n[Cancelled]';
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            AIChat.clearHistory();
            historyDiv.innerHTML = '';
            responseDiv.textContent = '';
        });
    }

    return {
        sendMessage,
        getHistory: () => AIChat.getHistory(),
        clearHistory: () => {
            AIChat.clearHistory();
            if (historyDiv) historyDiv.innerHTML = '';
        }
    };
}

// Export all classes
export default {
    MashupGenerator,
    HighConceptGenerator,
    RecommendationEngine,
    AIChat,
    AIService,
    createChatInterface
};
