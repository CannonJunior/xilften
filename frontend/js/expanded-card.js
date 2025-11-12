/**
 * Expanded Card Component
 * Wikipedia-style movie infobox with poster and detailed information
 */

import * as api from './api-client.js';

// Expanded card state
const cardState = {
    currentMedia: null,
    isOpen: false,
    container: null,
    currentView: 'info', // 'info' or 'soundtrack' - persists across movies
    soundtrackData: null,
    soundtrackCache: {} // Cache soundtracks by media_id
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
            // DON'T reset currentView - let it persist across movies

            // Render the appropriate view based on current selection
            if (cardState.currentView === 'soundtrack') {
                await loadSoundtrackView();
            } else {
                renderExpandedCard();
            }

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
        <div class="sidebar-view-toggle">
            <button class="view-toggle-btn ${cardState.currentView === 'info' ? 'active' : ''}" data-view="info">
                📄 Info
            </button>
            <button class="view-toggle-btn ${cardState.currentView === 'soundtrack' ? 'active' : ''}" data-view="soundtrack">
                🎵 Soundtrack
            </button>
        </div>
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

    // Setup view toggle listeners after rendering
    setupViewToggleListeners();
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
 * Setup listeners for view toggle buttons
 */
function setupViewToggleListeners() {
    const toggleButtons = document.querySelectorAll('.view-toggle-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const view = btn.dataset.view;
            await switchView(view);
        });
    });
}

/**
 * Switch between info and soundtrack views
 *
 * @param {string} view - View name ('info' or 'soundtrack')
 */
async function switchView(view) {
    if (cardState.currentView === view) return;

    cardState.currentView = view;

    if (view === 'soundtrack') {
        await loadSoundtrackView();
    } else {
        renderExpandedCard();
    }
}

/**
 * Load and render soundtrack view
 */
async function loadSoundtrackView() {
    try {
        const mediaId = cardState.currentMedia.id;
        console.log(`🎵 Loading soundtrack for: ${mediaId}`);

        const content = document.getElementById('movie-info-content');
        if (!content) return;

        // Check cache first
        if (cardState.soundtrackCache[mediaId]) {
            console.log('🎵 Using cached soundtrack data');
            cardState.soundtrackData = cardState.soundtrackCache[mediaId];
            renderSoundtrackView();
            return;
        }

        // Show loading state
        content.innerHTML = `
            <div class="sidebar-view-toggle">
                <button class="view-toggle-btn" data-view="info">
                    📄 Info
                </button>
                <button class="view-toggle-btn active" data-view="soundtrack">
                    🎵 Soundtrack
                </button>
            </div>
            <div class="soundtrack-loading">
                <p>Loading soundtrack...</p>
            </div>
        `;

        setupViewToggleListeners();

        // Fetch soundtrack data
        const response = await api.getSoundtrack(mediaId);

        if (response && response.length > 0) {
            const soundtrackData = response[0]; // Take first soundtrack
            // Cache the soundtrack data
            cardState.soundtrackCache[mediaId] = soundtrackData;
            cardState.soundtrackData = soundtrackData;
            renderSoundtrackView();
        } else {
            // Cache null to avoid refetching
            cardState.soundtrackCache[mediaId] = null;
            renderNoSoundtrack();
        }
    } catch (error) {
        console.error('❌ Failed to load soundtrack:', error);
        renderNoSoundtrack();
    }
}

/**
 * Render soundtrack view with tracks
 */
function renderSoundtrackView() {
    const content = document.getElementById('movie-info-content');
    if (!content || !cardState.soundtrackData) return;

    const soundtrack = cardState.soundtrackData;
    const tracks = soundtrack.tracks || [];

    // Format duration (milliseconds to mm:ss)
    const formatDuration = (ms) => {
        if (!ms) return '';
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    content.innerHTML = `
        <div class="sidebar-view-toggle">
            <button class="view-toggle-btn" data-view="info">
                📄 Info
            </button>
            <button class="view-toggle-btn active" data-view="soundtrack">
                🎵 Soundtrack
            </button>
        </div>
        <div class="soundtrack-container">
            <div class="soundtrack-header">
                <h2>${soundtrack.title}</h2>
                ${soundtrack.release_date ? `<p class="soundtrack-release-date">Released: ${new Date(soundtrack.release_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>` : ''}
                ${soundtrack.label ? `<p class="soundtrack-label">Label: ${soundtrack.label}</p>` : ''}
                ${soundtrack.total_tracks ? `<p class="soundtrack-track-count">${soundtrack.total_tracks} tracks</p>` : ''}
            </div>

            ${tracks.length > 0 ? `
            <div class="soundtrack-tracks">
                <h3>Track Listing</h3>
                <ol class="track-list">
                    ${tracks.map(track => `
                        <li class="track-item">
                            <div class="track-info">
                                <span class="track-title">${track.title}</span>
                                ${track.artist ? `<span class="track-artist">${track.artist}</span>` : ''}
                            </div>
                            ${track.duration_ms ? `<span class="track-duration">${formatDuration(track.duration_ms)}</span>` : ''}
                            ${track.preview_url ? `
                            <button class="track-play-btn" data-preview-url="${track.preview_url}" title="Play preview">
                                ▶️
                            </button>
                            ` : ''}
                        </li>
                    `).join('')}
                </ol>
            </div>
            ` : '<p class="soundtrack-empty">No tracks available</p>'}

            <div class="soundtrack-footer">
                ${soundtrack.spotify_album_id ? `
                <a href="https://open.spotify.com/album/${soundtrack.spotify_album_id}" target="_blank" class="spotify-link">
                    🎵 Open in Spotify
                </a>
                ` : ''}
                ${soundtrack.musicbrainz_id ? `
                <a href="https://musicbrainz.org/release/${soundtrack.musicbrainz_id}" target="_blank" class="musicbrainz-link">
                    📀 View on MusicBrainz
                </a>
                ` : ''}
            </div>
        </div>
    `;

    setupViewToggleListeners();
    setupTrackPlayButtons();
}

/**
 * Render no soundtrack message
 */
function renderNoSoundtrack() {
    const content = document.getElementById('movie-info-content');
    if (!content) return;

    const media = cardState.currentMedia;
    if (!media) return;

    // Extract year from release date
    const year = media.release_date ? new Date(media.release_date).getFullYear() : 'Unknown';

    content.innerHTML = `
        <div class="sidebar-view-toggle">
            <button class="view-toggle-btn" data-view="info">
                📄 Info
            </button>
            <button class="view-toggle-btn active" data-view="soundtrack">
                🎵 Soundtrack
            </button>
        </div>
        <div class="infobox">
            <div class="infobox-header">
                <h2>${media.title}</h2>
                ${media.original_title !== media.title ? `<p class="original-title">${media.original_title}</p>` : ''}
            </div>

            <!-- Soundtrack Meta Info -->
            <div class="sidebar-meta-info">
                ${media.release_date ? `
                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Year:</span>
                    <span class="sidebar-meta-value">${year}</span>
                </div>
                ` : ''}

                <div class="sidebar-meta-item">
                    <span class="sidebar-meta-label">Soundtrack Rating:</span>
                    <span class="sidebar-meta-value">—/10</span>
                </div>
            </div>

            <div class="soundtrack-empty-state">
                <p>🎵 No soundtrack data available for this movie.</p>
                <p class="soundtrack-empty-hint">Soundtracks are being continuously added to the database.</p>
            </div>
        </div>
    `;

    setupViewToggleListeners();
}

/**
 * Setup track play button listeners
 */
function setupTrackPlayButtons() {
    const playButtons = document.querySelectorAll('.track-play-btn');
    playButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const previewUrl = btn.dataset.previewUrl;
            if (previewUrl) {
                playTrackPreview(previewUrl);
            }
        });
    });
}

/**
 * Play track preview audio
 *
 * @param {string} previewUrl - Spotify preview URL
 */
function playTrackPreview(previewUrl) {
    // Simple audio preview playback
    // TODO: Implement proper audio player with controls
    const audio = new Audio(previewUrl);
    audio.play();
    console.log('🎵 Playing track preview:', previewUrl);
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

            // Render the appropriate view based on current selection
            // Same logic as showExpandedCard - persist the view
            if (cardState.currentView === 'soundtrack') {
                await loadSoundtrackView();
            } else {
                renderExpandedCard();
            }
            // Don't need to open again - it's already open
        }
    } catch (error) {
        console.error('❌ Failed to update media details:', error);
    }
}
