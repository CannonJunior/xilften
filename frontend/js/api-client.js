/**
 * API Client Module
 * Wrapper around fetch API for backend communication
 */

const API_BASE_URL = 'http://localhost:7575';

/**
 * Base API client configuration
 */
const defaultOptions = {
    headers: {
        'Content-Type': 'application/json',
    },
};

/**
 * Handle API response
 *
 * @param {Response} response - Fetch response object
 * @returns {Promise<Object>} - Parsed JSON response
 * @throws {Error} - If response is not ok
 */
async function handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error?.message || 'API request failed');
    }

    return data;
}

/**
 * Make GET request
 *
 * @param {string} endpoint - API endpoint
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} - API response data
 */
export async function get(endpoint, params = {}) {
    const url = new URL(`${API_BASE_URL}${endpoint}`);
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            url.searchParams.append(key, params[key]);
        }
    });

    const response = await fetch(url.toString(), {
        ...defaultOptions,
        method: 'GET',
    });

    return handleResponse(response);
}

/**
 * Make POST request
 *
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @returns {Promise<Object>} - API response data
 */
export async function post(endpoint, data = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        method: 'POST',
        body: JSON.stringify(data),
    });

    return handleResponse(response);
}

/**
 * Make PUT request
 *
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @returns {Promise<Object>} - API response data
 */
export async function put(endpoint, data = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        method: 'PUT',
        body: JSON.stringify(data),
    });

    return handleResponse(response);
}

/**
 * Make DELETE request
 *
 * @param {string} endpoint - API endpoint
 * @returns {Promise<Object>} - API response data
 */
export async function del(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        method: 'DELETE',
    });

    return handleResponse(response);
}

// ========== Media API Methods ==========

/**
 * Get all media with filters
 *
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} - Media list with pagination
 */
export async function getMedia(filters = {}) {
    return get('/api/media', filters);
}

/**
 * Get media by ID
 *
 * @param {string} mediaId - Media UUID
 * @returns {Promise<Object>} - Media details
 */
export async function getMediaById(mediaId) {
    return get(`/api/media/${mediaId}`);
}

/**
 * Search media
 *
 * @param {string} query - Search query
 * @param {number} page - Page number
 * @returns {Promise<Object>} - Search results
 */
export async function searchMedia(query, page = 1) {
    return get('/api/media/search', { q: query, page });
}

/**
 * Create new media
 *
 * @param {Object} mediaData - Media data
 * @returns {Promise<Object>} - Created media
 */
export async function createMedia(mediaData) {
    return post('/api/media', mediaData);
}

/**
 * Update media
 *
 * @param {string} mediaId - Media UUID
 * @param {Object} updates - Updated fields
 * @returns {Promise<Object>} - Updated media
 */
export async function updateMedia(mediaId, updates) {
    return put(`/api/media/${mediaId}`, updates);
}

/**
 * Delete media
 *
 * @param {string} mediaId - Media UUID
 * @returns {Promise<Object>} - Deletion result
 */
export async function deleteMedia(mediaId) {
    return del(`/api/media/${mediaId}`);
}

/**
 * Fetch media from TMDB
 *
 * @param {number} tmdbId - TMDB ID
 * @param {string} mediaType - 'movie' or 'tv'
 * @returns {Promise<Object>} - Fetched media
 */
export async function fetchFromTMDB(tmdbId, mediaType) {
    return post('/api/media/fetch-tmdb', { tmdb_id: tmdbId, media_type: mediaType });
}

// ========== Genre API Methods ==========

/**
 * Get all genres
 *
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} - Genre list
 */
export async function getGenres(filters = {}) {
    return get('/api/genres', filters);
}

/**
 * Get genre by ID
 *
 * @param {string} genreId - Genre UUID
 * @returns {Promise<Object>} - Genre details
 */
export async function getGenreById(genreId) {
    return get(`/api/genres/${genreId}`);
}

// ========== Calendar API Methods ==========

/**
 * Get calendar events
 *
 * @param {Object} filters - Date range and filters
 * @returns {Promise<Object>} - Events list
 */
export async function getCalendarEvents(filters = {}) {
    return get('/api/calendar/events', filters);
}

/**
 * Create calendar event
 *
 * @param {Object} eventData - Event data
 * @returns {Promise<Object>} - Created event
 */
export async function createCalendarEvent(eventData) {
    return post('/api/calendar/events', eventData);
}

/**
 * Update calendar event
 *
 * @param {string} eventId - Event UUID
 * @param {Object} updates - Updated fields
 * @returns {Promise<Object>} - Updated event
 */
export async function updateCalendarEvent(eventId, updates) {
    return put(`/api/calendar/events/${eventId}`, updates);
}

/**
 * Delete calendar event
 *
 * @param {string} eventId - Event UUID
 * @returns {Promise<Object>} - Deletion result
 */
export async function deleteCalendarEvent(eventId) {
    return del(`/api/calendar/events/${eventId}`);
}

/**
 * Mark event as complete
 *
 * @param {string} eventId - Event UUID
 * @returns {Promise<Object>} - Updated event
 */
export async function completeCalendarEvent(eventId) {
    return post(`/api/calendar/events/${eventId}/complete`);
}

// ========== Recommendation API Methods ==========

/**
 * Generate recommendations
 *
 * @param {Object} params - Criteria preset and options
 * @returns {Promise<Object>} - Recommendations list
 */
export async function getRecommendations(params = {}) {
    return post('/api/recommendations/generate', params);
}

/**
 * Get similar media
 *
 * @param {string} mediaId - Media UUID
 * @param {number} limit - Number of results
 * @returns {Promise<Object>} - Similar media list
 */
export async function getSimilarMedia(mediaId, limit = 10) {
    return get(`/api/recommendations/similar/${mediaId}`, { limit });
}

// ========== Criteria API Methods ==========

/**
 * Get all criteria presets
 *
 * @returns {Promise<Array>} - Presets list
 */
export async function getCriteriaPresets() {
    return get('/api/recommendations/presets');
}

/**
 * Get criteria preset by ID
 *
 * @param {string} presetId - Preset UUID
 * @returns {Promise<Object>} - Preset details
 */
export async function getCriteriaPreset(presetId) {
    return get(`/api/recommendations/presets/${presetId}`);
}

/**
 * Create criteria preset
 *
 * @param {Object} presetData - Preset configuration
 * @returns {Promise<Object>} - Created preset
 */
export async function createCriteriaPreset(presetData) {
    return post('/api/recommendations/presets', presetData);
}

/**
 * Update criteria preset
 *
 * @param {string} presetId - Preset UUID
 * @param {Object} updates - Updated configuration
 * @returns {Promise<Object>} - Updated preset
 */
export async function updateCriteriaPreset(presetId, updates) {
    return put(`/api/recommendations/presets/${presetId}`, updates);
}

/**
 * Delete criteria preset
 *
 * @param {string} presetId - Preset UUID
 * @returns {Promise<void>}
 */
export async function deleteCriteriaPreset(presetId) {
    return del(`/api/recommendations/presets/${presetId}`);
}

/**
 * Get available criteria fields
 *
 * @returns {Promise<Object>} - Available fields with categories
 */
export async function getAvailableFields() {
    return get('/api/recommendations/available-fields');
}

// ========== AI API Methods ==========

/**
 * Generate content mashup
 *
 * @param {string} query - User query
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} - Mashup recommendations
 */
export async function generateMashup(query, options = {}) {
    return post('/api/ai/mashup', { query, ...options });
}

/**
 * Generate high-concept summary
 *
 * @param {Array} referenceMedia - Reference media with attributes
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} - Generated concept
 */
export async function generateHighConcept(referenceMedia, options = {}) {
    return post('/api/ai/high-concept', { reference_media: referenceMedia, ...options });
}

/**
 * Chat with AI
 *
 * @param {string} message - User message
 * @param {Object} options - Chat options
 * @returns {Promise<Object>} - AI response
 */
export async function chatWithAI(message, options = {}) {
    return post('/api/ai/chat', { user_message: message, ...options });
}

/**
 * Get AI model status
 *
 * @returns {Promise<Object>} - Model status
 */
export async function getAIStatus() {
    return get('/api/ai/status');
}

// ========== Review API Methods ==========

/**
 * Get reviews for media
 *
 * @param {string} mediaId - Media UUID
 * @returns {Promise<Object>} - Reviews list
 */
export async function getMediaReviews(mediaId) {
    return get(`/api/reviews/media/${mediaId}`);
}

/**
 * Create review
 *
 * @param {Object} reviewData - Review data
 * @returns {Promise<Object>} - Created review
 */
export async function createReview(reviewData) {
    return post('/api/reviews', reviewData);
}

/**
 * Update review
 *
 * @param {string} reviewId - Review UUID
 * @param {Object} updates - Updated fields
 * @returns {Promise<Object>} - Updated review
 */
export async function updateReview(reviewId, updates) {
    return put(`/api/reviews/${reviewId}`, updates);
}

/**
 * Delete review
 *
 * @param {string} reviewId - Review UUID
 * @returns {Promise<Object>} - Deletion result
 */
export async function deleteReview(reviewId) {
    return del(`/api/reviews/${reviewId}`);
}

// ========== Health & Utility Methods ==========

/**
 * Check API health
 *
 * @returns {Promise<Object>} - Health status
 */
export async function checkHealth() {
    return get('/api/health');
}

/**
 * Get API version
 *
 * @returns {Promise<Object>} - Version info
 */
export async function getVersion() {
    return get('/api/version');
}

export default {
    // Core methods
    get,
    post,
    put,
    del,

    // Media
    getMedia,
    getMediaById,
    searchMedia,
    createMedia,
    updateMedia,
    deleteMedia,
    fetchFromTMDB,

    // Genres
    getGenres,
    getGenreById,

    // Calendar
    getCalendarEvents,
    createCalendarEvent,
    updateCalendarEvent,
    deleteCalendarEvent,
    completeCalendarEvent,

    // Recommendations
    getRecommendations,
    getSimilarMedia,

    // Criteria
    getCriteriaPresets,
    createCriteriaPreset,
    updateCriteriaPreset,
    deleteCriteriaPreset,
    getAvailableFields,

    // AI
    generateMashup,
    generateHighConcept,
    chatWithAI,
    getAIStatus,

    // Reviews
    getMediaReviews,
    createReview,
    updateReview,
    deleteReview,

    // Health
    checkHealth,
    getVersion,
};
