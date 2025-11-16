/**
 * Audio Catalog Module
 * Manages audio content browsing with D3.js carousel
 */

// Audio catalog state
let audioCatalogState = {
    albums: [],
    genres: [],
    currentGenre: '',
    searchQuery: '',
    isLoading: false,
};

/**
 * Initialize audio catalog
 */
export async function initAudioCatalog() {
    console.log('🎵 Initializing audio catalog...');

    // Load genres for filter
    await loadAudioGenres();

    // Setup event listeners
    setupAudioEventListeners();

    // Load initial albums
    await loadAlbums();

    console.log('✨ Audio catalog initialized!');
}

/**
 * Load audio genres from API
 */
async function loadAudioGenres() {
    try {
        const response = await fetch('/api/audio/genres');
        const data = await response.json();

        if (data.success) {
            audioCatalogState.genres = data.data.items || [];
            populateGenreFilter();
            console.log(`✅ Loaded ${audioCatalogState.genres.length} audio genres`);
        }
    } catch (error) {
        console.error('❌ Error loading audio genres:', error);
    }
}

/**
 * Populate genre filter dropdown
 */
function populateGenreFilter() {
    const genreFilter = document.getElementById('audio-genre-filter');
    if (!genreFilter) return;

    // Clear existing options except "All Genres"
    genreFilter.innerHTML = '<option value="">All Genres</option>';

    // Add genre options
    audioCatalogState.genres.forEach(genre => {
        const option = document.createElement('option');
        option.value = genre.id;
        option.textContent = genre.name;
        genreFilter.appendChild(option);
    });
}

/**
 * Setup event listeners for audio catalog
 */
function setupAudioEventListeners() {
    // Genre filter
    const genreFilter = document.getElementById('audio-genre-filter');
    if (genreFilter) {
        genreFilter.addEventListener('change', (e) => {
            audioCatalogState.currentGenre = e.target.value;
            loadAlbums();
        });
    }

    // Search input
    const searchInput = document.getElementById('search-audio');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                audioCatalogState.searchQuery = e.target.value;
                loadAlbums();
            }, 300); // Debounce search
        });
    }
}

/**
 * Load albums from API
 */
async function loadAlbums() {
    if (audioCatalogState.isLoading) return;

    audioCatalogState.isLoading = true;
    showLoadingState();

    try {
        // Build query parameters
        const params = new URLSearchParams({
            page: 1,
            page_size: 50,
        });

        if (audioCatalogState.currentGenre) {
            params.append('genre_id', audioCatalogState.currentGenre);
        }

        if (audioCatalogState.searchQuery) {
            params.append('search', audioCatalogState.searchQuery);
        }

        const response = await fetch(`/api/audio/albums?${params}`);
        const data = await response.json();

        if (data.success) {
            audioCatalogState.albums = data.data.items || [];
            updateAlbumCount(audioCatalogState.albums.length);
            renderAlbumCarousel(audioCatalogState.albums);
            console.log(`✅ Loaded ${audioCatalogState.albums.length} albums`);
        } else {
            showErrorState('Failed to load albums');
        }
    } catch (error) {
        console.error('❌ Error loading albums:', error);
        showErrorState('Error loading albums');
    } finally {
        audioCatalogState.isLoading = false;
    }
}

/**
 * Update album count badge
 *
 * @param {number} count - Number of albums
 */
function updateAlbumCount(count) {
    const countElement = document.getElementById('audio-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    const container = document.getElementById('audio-catalog');
    if (!container) return;

    container.innerHTML = `
        <div class="carousel-count-badge">
            <span id="audio-count">0</span> albums
        </div>
        <p class="loading-message">Loading audio catalog...</p>
    `;
}

/**
 * Show error state
 *
 * @param {string} message - Error message
 */
function showErrorState(message) {
    const container = document.getElementById('audio-catalog');
    if (!container) return;

    container.innerHTML = `
        <div class="carousel-count-badge">
            <span id="audio-count">0</span> albums
        </div>
        <p class="error-message">${message}</p>
    `;
}

/**
 * Show empty state
 */
function showEmptyState() {
    const container = document.getElementById('audio-catalog');
    if (!container) return;

    const message = audioCatalogState.searchQuery || audioCatalogState.currentGenre
        ? 'No albums found matching your filters'
        : 'No albums in the catalog yet';

    container.innerHTML = `
        <div class="carousel-count-badge">
            <span id="audio-count">0</span> albums
        </div>
        <p class="empty-message">${message}</p>
    `;
}

/**
 * Render album carousel with D3.js
 *
 * @param {Array} albums - Album items to display
 */
function renderAlbumCarousel(albums) {
    console.log('🎵 Rendering album carousel with', albums.length, 'albums');

    if (!albums || albums.length === 0) {
        showEmptyState();
        return;
    }

    const container = d3.select('#audio-catalog');

    // Remove only the carousel wrapper, preserve the count badge
    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.empty-message').remove();
    container.selectAll('.loading-message').remove();
    container.selectAll('.error-message').remove();

    // Create carousel structure with horizontal scrolling
    const carouselWrapper = container
        .append('div')
        .attr('class', 'carousel-wrapper')
        .style('display', 'flex')
        .style('gap', '24px')
        .style('padding', '40px')
        .style('overflow-x', 'auto')
        .style('overflow-y', 'hidden')
        .style('scroll-behavior', 'smooth')
        .style('-webkit-overflow-scrolling', 'touch')
        .style('scrollbar-width', 'thin')
        .style('scrollbar-color', '#6366f1 #2a2a3e');

    // Render items as HTML divs
    const itemDivs = carouselWrapper
        .selectAll('.carousel-item')
        .data(albums, d => d.id)
        .enter()
        .append('div')
        .attr('class', 'carousel-item audio-album-card')
        .attr('data-album-id', d => d.id)
        .style('min-width', '280px')
        .style('flex-shrink', '0')
        .style('cursor', 'pointer')
        .style('opacity', 0);

    // Animate entrance
    itemDivs
        .transition()
        .duration(300)
        .delay((d, i) => i * 50)
        .style('opacity', 1);

    // Build each album card
    itemDivs.each(function(d) {
        const card = d3.select(this);

        // Album cover art
        const coverUrl = d.cover_art_url || d.cover_art_small_url || '/static/images/default-album.png';

        card.append('div')
            .attr('class', 'album-cover')
            .style('width', '280px')
            .style('height', '280px')
            .style('background-image', `url(${coverUrl})`)
            .style('background-size', 'cover')
            .style('background-position', 'center')
            .style('border-radius', '8px')
            .style('margin-bottom', '12px')
            .style('box-shadow', '0 4px 6px rgba(0, 0, 0, 0.3)');

        // Album info container
        const infoContainer = card.append('div')
            .attr('class', 'album-info')
            .style('padding', '0 8px');

        // Album title
        infoContainer.append('h3')
            .attr('class', 'album-title')
            .style('font-size', '16px')
            .style('font-weight', '600')
            .style('color', '#e5e7eb')
            .style('margin', '0 0 4px 0')
            .style('white-space', 'nowrap')
            .style('overflow', 'hidden')
            .style('text-overflow', 'ellipsis')
            .text(d.title);

        // Artist name
        if (d.primary_artist) {
            infoContainer.append('p')
                .attr('class', 'album-artist')
                .style('font-size', '14px')
                .style('color', '#9ca3af')
                .style('margin', '0 0 4px 0')
                .style('white-space', 'nowrap')
                .style('overflow', 'hidden')
                .style('text-overflow', 'ellipsis')
                .text(d.primary_artist.name || 'Unknown Artist');
        }

        // Album metadata (year, tracks, type)
        const metadataItems = [];

        if (d.release_year) {
            metadataItems.push(d.release_year);
        }

        if (d.total_tracks) {
            metadataItems.push(`${d.total_tracks} tracks`);
        }

        if (d.content_type && d.content_type !== 'album') {
            metadataItems.push(d.content_type.toUpperCase());
        }

        if (metadataItems.length > 0) {
            infoContainer.append('p')
                .attr('class', 'album-metadata')
                .style('font-size', '12px')
                .style('color', '#6b7280')
                .style('margin', '0')
                .text(metadataItems.join(' • '));
        }

        // Click handler (future: expand album details)
        card.on('click', () => {
            console.log('🎵 Album clicked:', d.title);
            // TODO: Implement album detail view
        });

        // Hover effect
        card
            .on('mouseenter', function() {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style('transform', 'translateY(-8px)');
            })
            .on('mouseleave', function() {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style('transform', 'translateY(0)');
            });
    });

    console.log('✅ Album carousel rendered successfully');
}

/**
 * Refresh audio catalog (called when view becomes visible)
 */
export function refreshAudioCatalog() {
    console.log('🔄 Refreshing audio catalog...');
    loadAlbums();
}
