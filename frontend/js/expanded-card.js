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

    // Create card container
    createCardContainer();

    // Setup global click listener for media items
    setupClickListeners();

    console.log('✅ Expanded Card initialized');
}

/**
 * Create card container element
 */
function createCardContainer() {
    const existing = document.getElementById('expanded-card-overlay');
    if (existing) {
        existing.remove();
    }

    const overlay = document.createElement('div');
    overlay.id = 'expanded-card-overlay';
    overlay.className = 'expanded-card-overlay';
    overlay.style.display = 'none';

    overlay.innerHTML = `
        <div class="expanded-card-container">
            <button class="expanded-card-close" aria-label="Close">&times;</button>
            <div class="expanded-card-content">
                <!-- Content will be populated dynamically -->
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    cardState.container = overlay;

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeExpandedCard();
        }
    });

    // Close button
    overlay.querySelector('.expanded-card-close').addEventListener('click', closeExpandedCard);

    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && cardState.isOpen) {
            closeExpandedCard();
        }
    });
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

    const content = cardState.container.querySelector('.expanded-card-content');

    // Get TMDB data from custom fields
    const tmdbData = media.custom_fields?.tmdb_data || {};

    // Build poster URL
    const posterUrl = media.poster_path
        ? `https://image.tmdb.org/t/p/w500${media.poster_path}`
        : 'https://via.placeholder.com/300x450?text=No+Poster';

    // Format budget and box office
    const formatCurrency = (amount) => {
        if (!amount) return 'Unknown';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0
        }).format(amount);
    };

    content.innerHTML = `
        <div class="infobox">
            <div class="infobox-header">
                <h2>${media.title}</h2>
                ${media.original_title !== media.title ? `<p class="original-title">${media.original_title}</p>` : ''}
            </div>

            <div class="infobox-image">
                <img src="${posterUrl}" alt="${media.title} poster" />
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
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
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
        document.body.style.overflow = ''; // Restore scrolling
    }
}
