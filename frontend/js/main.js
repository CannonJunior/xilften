/**
 * Main Application Module
 * App initialization, navigation, and global state management
 */

import * as api from './api-client.js';
import * as recommendations from './recommendations.js';
import * as criteriaBuilder from './criteria-builder.js';
import { init3DVisualization } from './3d-criteria-viz.js';
import { initPersonaManager } from './persona-manager.js';
import { initExpandedCard } from './expanded-card.js';

/**
 * Application state
 */
const appState = {
    currentView: 'carousel',
    media: [],
    selectedMedia: null,
    filters: {
        genre: '',
        search: '',
    },
};

/**
 * Initialize application
 */
async function initApp() {
    console.log('🚀 Initializing XILFTEN...');

    // Check API health
    try {
        const health = await api.checkHealth();
        console.log('✅ API Health:', health);
    } catch (error) {
        console.error('❌ API Health Check Failed:', error);
        showError('Failed to connect to backend API. Please ensure the server is running on port 7575.');
        return;
    }

    // Setup navigation
    setupNavigation();

    // Initialize modules
    await criteriaBuilder.init();

    // Initialize persona manager
    await initPersonaManager();

    // Initialize expanded card
    initExpandedCard();

    // Load genres for filter
    await loadGenres();

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    await loadInitialData();

    // Show default view
    showView('carousel');

    console.log('✨ XILFTEN initialized successfully!');
}

/**
 * Setup navigation between views
 */
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-button');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const view = button.dataset.view;
            showView(view);

            // Update active state
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
}

/**
 * Show specific view
 *
 * @param {string} viewName - View name ('carousel', 'calendar', 'recommendations', 'ai')
 */
function showView(viewName) {
    appState.currentView = viewName;

    // Hide all views
    document.querySelectorAll('.view-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected view
    const viewId = `${viewName}-view`;
    const viewElement = document.getElementById(viewId);
    if (viewElement) {
        viewElement.classList.add('active');

        // Trigger view-specific initialization
        initializeView(viewName);
    }
}

/**
 * Initialize view-specific functionality
 *
 * @param {string} viewName - View name
 */
async function initializeView(viewName) {
    switch (viewName) {
        case 'carousel':
            // Carousel initialization handled by carousel.js
            console.log('📽️ Initializing carousel view...');
            break;
        case 'recommendations':
            console.log('⭐ Initializing recommendations view...');
            await recommendations.init();
            break;
        case 'ai':
            console.log('🤖 Initializing AI assistant view...');
            break;
        case 'criteria-3d':
            console.log('🎬 Initializing 3D visualization...');
            init3DVisualization();
            break;
    }
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Genre filter
    const genreFilter = document.getElementById('filter-genre');
    if (genreFilter) {
        genreFilter.addEventListener('change', async (e) => {
            appState.filters.genre = e.target.value;
            await loadMedia();
        });
    }

    // Search input
    const searchInput = document.getElementById('search-media');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(async () => {
                appState.filters.search = e.target.value;
                await loadMedia();
            }, 500); // Debounce 500ms
        });
    }

    // AI preset queries
    const presetButtons = document.querySelectorAll('.preset-button');
    presetButtons.forEach(button => {
        button.addEventListener('click', () => {
            const query = button.dataset.query;
            document.getElementById('chat-input').value = query;
        });
    });

    // AI send message
    const sendButton = document.getElementById('send-message');
    const chatInput = document.getElementById('chat-input');
    if (sendButton && chatInput) {
        sendButton.addEventListener('click', () => sendAIMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAIMessage();
            }
        });
    }
}

/**
 * Load genres and populate filter dropdown
 */
async function loadGenres() {
    console.log('🎭 Loading genres...');

    try {
        const response = await api.getGenres();

        if (response.success && response.data) {
            const genres = response.data;
            const genreFilter = document.getElementById('filter-genre');

            if (genreFilter) {
                // Clear existing options except "All Genres"
                genreFilter.innerHTML = '<option value="">All Genres</option>';

                // Get parent genres only (genres without parent_genre_id)
                const parentGenres = genres.filter(g => !g.parent_genre_id && g.is_active);

                // Sort alphabetically
                parentGenres.sort((a, b) => a.name.localeCompare(b.name));

                // Add genre options
                parentGenres.forEach(genre => {
                    const option = document.createElement('option');
                    option.value = genre.slug;
                    option.textContent = genre.name;
                    genreFilter.appendChild(option);
                });

                console.log(`✅ Loaded ${parentGenres.length} genres`);
            }
        }
    } catch (error) {
        console.error('❌ Failed to load genres:', error);
    }
}

/**
 * Load initial data
 */
async function loadInitialData() {
    console.log('📚 Loading initial data...');

    try {
        await loadMedia();
        console.log('✅ Initial data loaded');
    } catch (error) {
        console.error('❌ Failed to load initial data:', error);
        showError('Failed to load media data. Please refresh the page.');
    }
}

/**
 * Load media with current filters
 */
async function loadMedia() {
    try {
        showLoading('media-carousel');

        const params = {
            page: 1,
            page_size: 500,
        };

        if (appState.filters.genre) {
            params.genre = appState.filters.genre;
        }

        if (appState.filters.search) {
            // Use search endpoint if search query exists
            const response = await api.searchMedia(appState.filters.search);
            appState.media = response.data.items || [];
        } else {
            // Use regular media endpoint with filters
            const response = await api.getMedia(params);
            appState.media = response.data.items || [];
        }

        console.log(`📊 Loaded ${appState.media.length} media items`);

        // Trigger carousel render if on carousel view
        if (appState.currentView === 'carousel') {
            renderCarousel(appState.media);
        }

    } catch (error) {
        console.error('❌ Failed to load media:', error);
        showError('Failed to load media. Using sample data.', 'media-carousel');

        // Load sample data for development
        loadSampleData();
    }
}

/**
 * Load sample data for development
 */
function loadSampleData() {
    appState.media = [
        {
            id: '1',
            title: 'The Matrix',
            media_type: 'movie',
            release_date: '1999-03-31',
            runtime: 136,
            tmdb_rating: 8.7,
            poster_path: '/placeholder-matrix.jpg',
            genres: ['sci-fi', 'action'],
        },
        {
            id: '2',
            title: 'Blade Runner',
            media_type: 'movie',
            release_date: '1982-06-25',
            runtime: 117,
            tmdb_rating: 8.1,
            poster_path: '/placeholder-blade-runner.jpg',
            genres: ['sci-fi', 'tech-noir'],
        },
        {
            id: '3',
            title: 'Spirited Away',
            media_type: 'movie',
            release_date: '2001-07-20',
            runtime: 125,
            tmdb_rating: 8.6,
            poster_path: '/placeholder-spirited-away.jpg',
            genres: ['anime', 'fantasy'],
        },
    ];

    if (appState.currentView === 'carousel') {
        renderCarousel(appState.media);
    }
}

/**
 * Render carousel with media
 * (Actual D3 rendering handled by carousel.js)
 *
 * @param {Array} media - Media items
 */
function renderCarousel(media) {
    const container = document.getElementById('media-carousel');
    if (!container) return;

    if (media.length === 0) {
        container.innerHTML = '<p class="empty-message">No media found matching your filters.</p>';
        return;
    }

    // Dispatch custom event for carousel module to handle
    const event = new CustomEvent('carouselDataReady', { detail: { media } });
    window.dispatchEvent(event);
}

/**
 * Load recommendations
 */
async function loadRecommendations() {
    try {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        showLoading('recommendations-container');

        // For now, show empty message
        container.innerHTML = '<p class="empty-message">Select a criteria preset or create your own to get recommendations.</p>';

    } catch (error) {
        console.error('❌ Failed to load recommendations:', error);
        showError('Failed to load recommendations.', 'recommendations-container');
    }
}

/**
 * Send AI message
 */
async function sendAIMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatInput || !chatMessages) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    appendChatMessage('user', message);
    chatInput.value = '';

    try {
        // Show typing indicator
        const typingId = appendChatMessage('assistant', 'Thinking...');

        // Call AI API
        const response = await api.chatWithAI(message);

        // Remove typing indicator
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }

        // Add AI response with poster gallery if available
        const posterGalleryHtml = response.data.metadata?.poster_gallery_html || '';
        appendChatMessage('assistant', response.data.content, posterGalleryHtml);

    } catch (error) {
        console.error('❌ AI request failed:', error);
        appendChatMessage('assistant', 'Sorry, I encountered an error. Please make sure Ollama is running and try again.');
    }
}

/**
 * Append message to chat
 *
 * @param {string} role - 'user' or 'assistant'
 * @param {string} content - Message content
 * @param {string} posterGalleryHtml - Optional HTML for poster gallery
 * @returns {string} - Message element ID
 */
function appendChatMessage(role, content, posterGalleryHtml = '') {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convert markdown-style content to HTML
    const htmlContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    contentDiv.innerHTML = `<p>${htmlContent}</p>`;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.appendChild(contentDiv);

    // Add poster gallery if provided
    if (posterGalleryHtml) {
        const galleryDiv = document.createElement('div');
        galleryDiv.className = 'poster-gallery-container';
        galleryDiv.innerHTML = posterGalleryHtml;
        messageDiv.appendChild(galleryDiv);

        // Add drag event listeners to all poster images
        setTimeout(() => {
            const posters = galleryDiv.querySelectorAll('.ai-poster-image[draggable="true"]');
            posters.forEach(poster => {
                poster.addEventListener('dragstart', handlePosterDragStart);
                poster.addEventListener('drag', handlePosterDrag);
                poster.addEventListener('dragend', handlePosterDragEnd);
            });
        }, 100);
    }

    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}

/**
 * Handle drag start for AI poster images
 */
function handlePosterDragStart(event) {
    const mediaId = event.target.dataset.mediaId;
    const mediaTitle = event.target.dataset.mediaTitle;

    console.log('🎬 AI POSTER DRAG START - Movie:', mediaTitle, 'ID:', mediaId);

    event.dataTransfer.setData('mediaId', mediaId);
    event.dataTransfer.setData('mediaTitle', mediaTitle);
    event.dataTransfer.effectAllowed = 'copy';
}

/**
 * Handle drag for AI poster images
 */
function handlePosterDrag(event) {
    console.log('🎬 AI POSTER DRAGGING...');
}

/**
 * Handle drag end for AI poster images
 */
function handlePosterDragEnd(event) {
    console.log('🎬 AI POSTER DRAG END');
}

/**
 * Show loading state
 *
 * @param {string} containerId - Container element ID
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        // For media-carousel, preserve the count badge
        if (containerId === 'media-carousel') {
            // Remove existing content except count badge
            const countBadge = container.querySelector('.carousel-count-badge');
            container.innerHTML = '';

            // Re-add count badge if it existed
            if (countBadge) {
                container.appendChild(countBadge);
            }

            // Add loading message
            const loadingMsg = document.createElement('p');
            loadingMsg.className = 'loading-message';
            loadingMsg.textContent = 'Loading';
            container.appendChild(loadingMsg);
        } else {
            container.innerHTML = '<p class="loading-message">Loading</p>';
        }
    }
}

/**
 * Show error message
 *
 * @param {string} message - Error message
 * @param {string} containerId - Container element ID (optional)
 */
function showError(message, containerId = null) {
    console.error(message);

    if (containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            // For media-carousel, preserve the count badge
            if (containerId === 'media-carousel') {
                // Remove existing content except count badge
                const countBadge = container.querySelector('.carousel-count-badge');
                container.innerHTML = '';

                // Re-add count badge if it existed
                if (countBadge) {
                    container.appendChild(countBadge);
                }

                // Add error message
                const errorMsg = document.createElement('p');
                errorMsg.className = 'empty-message';
                errorMsg.style.color = 'var(--color-error)';
                errorMsg.textContent = message;
                container.appendChild(errorMsg);
            } else {
                container.innerHTML = `<p class="empty-message" style="color: var(--color-error);">${message}</p>`;
            }
        }
    } else {
        // TODO: Implement global toast notification
        alert(message);
    }
}

/**
 * Format date
 *
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date
 */
export function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Format runtime
 *
 * @param {number} minutes - Runtime in minutes
 * @returns {string} - Formatted runtime (e.g., "2h 16m")
 */
export function formatRuntime(minutes) {
    if (!minutes) return '';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// Export state and functions for other modules
export { appState, showView, showError, showLoading };
