/**
 * Expanded Card Component
 * Wikipedia-style movie infobox with poster and detailed information
 */

import * as api from './api-client.js';

// Expanded card state
const cardState = {
    currentMedia: null,
    isOpen: false,
    container: null
};

/**
 * Initialize expanded card functionality
 */
export function initExpandedCard() {
    console.log('🎬 Initializing Expanded Card...');

    // Get reference to sidebar
    cardState.container = document.getElementById('movie-info-sidebar');

    // Setup global click listener for media items
    setupClickListeners();

    // Setup close button
    const closeButton = cardState.container?.querySelector('.sidebar-close');
    if (closeButton) {
        closeButton.addEventListener('click', closeExpandedCard);
    }

    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && cardState.isOpen) {
            closeExpandedCard();
        }
    });

    // Listen for carousel scroll events
    setupCarouselScrollListener();

    console.log('✅ Expanded Card initialized');
}

/**
 * Setup click listeners for media items
 */
function setupClickListeners() {
    // Delegate click events to media elements
    document.addEventListener('click', async (e) => {
        const mediaElement = e.target.closest('[data-media-id]');
        if (mediaElement) {
            const mediaId = mediaElement.dataset.mediaId;
            await showExpandedCard(mediaId);
        }
    });
}

/**
 * Show expanded card for a media item
 *
 * @param {string} mediaId - Media UUID
 */
export async function showExpandedCard(mediaId) {
    try {
        console.log(`🎬 Loading expanded card for: ${mediaId}`);

        // Fetch media details
        const response = await api.getMediaById(mediaId);

        if (response.success) {
            cardState.currentMedia = response.data;
            renderExpandedCard();
            openExpandedCard();
        }
    } catch (error) {
        console.error('❌ Failed to load media details:', error);
    }
}

/**
 * Render expanded card content
 */
function renderExpandedCard() {
    const media = cardState.currentMedia;
    if (!media) return;

    const content = document.getElementById('movie-info-content');
    if (!content) return;

    // Get TMDB data from custom fields
    const tmdbData = media.custom_fields?.tmdb_data || {};

    // Format budget and box office
    const formatCurrency = (amount) => {
        if (!amount) return 'Unknown';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0
        }).format(amount);
    };

    // Format runtime
    const formatRuntime = (minutes) => {
        if (!minutes) return '';
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    };

    // Get TMDB image URL
    const getTMDBImageURL = (path, size = 'w500') => {
        if (!path) return '';
        return `https://image.tmdb.org/t/p/${size}${path}`;
    };

    content.innerHTML = `
        <div class="infobox">
            <div class="infobox-header">
                <h2>${media.title}</h2>
                ${media.original_title !== media.title ? `<p class="original-title">${media.original_title}</p>` : ''}
            </div>

            <!-- Media Info Section -->
            <div class="sidebar-meta-info">
                ${media.release_date ? `
                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Year:</span>
                    <span class="sidebar-meta-value">${new Date(media.release_date).getFullYear()}</span>
                </div>
                ` : ''}

                ${media.runtime ? `
                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Runtime:</span>
                    <span class="sidebar-meta-value">${formatRuntime(media.runtime)}</span>
                </div>
                ` : ''}

                ${media.tmdb_rating ? `
                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Rating:</span>
                    <span class="sidebar-meta-value">⭐ ${parseFloat(media.tmdb_rating).toFixed(1)}/10</span>
                </div>
                ` : ''}

                ${media.genres && media.genres.length > 0 ? `
                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Genres:</span>
                    <div class="sidebar-genre-tags">
                        ${media.genres.map(genre =>
                            `<span class="sidebar-genre-tag">${typeof genre === 'string' ? genre : genre.name}</span>`
                        ).join('')}
                    </div>
                </div>
                ` : ''}
            </div>

            <table class="infobox-table">
                <tbody>
                    ${media.tagline ? `
                    <tr>
                        <th colspan="2" class="infobox-tagline">"${media.tagline}"</th>
                    </tr>
                    ` : ''}

                    ${tmdbData.director ? `
                    <tr>
                        <th>Directed by</th>
                        <td>${tmdbData.director}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.screenplay ? `
                    <tr>
                        <th>Screenplay by</th>
                        <td>${tmdbData.screenplay}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.starring ? `
                    <tr>
                        <th>Starring</th>
                        <td>${tmdbData.starring}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.cinematography ? `
                    <tr>
                        <th>Cinematography</th>
                        <td>${tmdbData.cinematography}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.music ? `
                    <tr>
                        <th>Music by</th>
                        <td>${tmdbData.music}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.editing ? `
                    <tr>
                        <th>Edited by</th>
                        <td>${tmdbData.editing}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.production_companies ? `
                    <tr>
                        <th>Production<br>companies</th>
                        <td>${tmdbData.production_companies}</td>
                    </tr>
                    ` : ''}

                    ${media.release_date ? `
                    <tr>
                        <th>Release date</th>
                        <td>${new Date(media.release_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</td>
                    </tr>
                    ` : ''}

                    ${media.runtime ? `
                    <tr>
                        <th>Running time</th>
                        <td>${media.runtime} minutes</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.languages ? `
                    <tr>
                        <th>Languages</th>
                        <td>${tmdbData.languages}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.budget ? `
                    <tr>
                        <th>Budget</th>
                        <td>${formatCurrency(tmdbData.budget)}</td>
                    </tr>
                    ` : ''}

                    ${tmdbData.box_office ? `
                    <tr>
                        <th>Box office</th>
                        <td>${formatCurrency(tmdbData.box_office)}</td>
                    </tr>
                    ` : ''}

                    ${media.tmdb_rating ? `
                    <tr>
                        <th>TMDB Rating</th>
                        <td>${media.tmdb_rating} / 10</td>
                    </tr>
                    ` : ''}
                </tbody>
            </table>

            ${media.overview ? `
            <div class="infobox-overview">
                <h3>Overview</h3>
                <p>${media.overview}</p>
            </div>
            ` : ''}

            ${media.custom_fields?.storytelling ? `
            <div class="infobox-criteria">
                <h3>Criteria Scores</h3>
                <div class="criteria-scores">
                    <div class="criteria-score">
                        <span class="criteria-label" style="color: #ef4444;">Storytelling</span>
                        <span class="criteria-value">${media.custom_fields.storytelling}/10</span>
                    </div>
                    <div class="criteria-score">
                        <span class="criteria-label" style="color: #10b981;">Characters</span>
                        <span class="criteria-value">${media.custom_fields.characters}/10</span>
                    </div>
                    <div class="criteria-score">
                        <span class="criteria-label" style="color: #3b82f6;">Vision</span>
                        <span class="criteria-value">${media.custom_fields.cohesive_vision}/10</span>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

/**
 * Open expanded card
 */
function openExpandedCard() {
    if (cardState.container) {
        cardState.container.style.display = 'flex';
        cardState.isOpen = true;
    }
}

/**
 * Close expanded card
 */
function closeExpandedCard() {
    if (cardState.container) {
        cardState.container.style.display = 'none';
        cardState.isOpen = false;
        cardState.currentMedia = null;
    }
}

/**
 * Setup listener for carousel scroll events
 */
function setupCarouselScrollListener() {
    window.addEventListener('carouselItemInView', async (event) => {
        // Only update if sidebar is currently open
        if (!cardState.isOpen) {
            return;
        }

        const { mediaId } = event.detail;

        // Only update if this is a different media item
        if (cardState.currentMedia?.id !== mediaId) {
            console.log(`🔄 Carousel scrolled to new item: ${mediaId}`);
            await updateExpandedCard(mediaId);
        }
    });
}

/**
 * Update expanded card with new media (without fetching again if already open)
 *
 * @param {string} mediaId - Media UUID
 */
async function updateExpandedCard(mediaId) {
    try {
        // Fetch media details
        const response = await api.getMediaById(mediaId);

        if (response.success) {
            cardState.currentMedia = response.data;
            renderExpandedCard();
            // Don't need to open again - it's already open
        }
    } catch (error) {
        console.error('❌ Failed to update media details:', error);
    }
}
