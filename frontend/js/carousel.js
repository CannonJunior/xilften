/**
 * Carousel Module
 * D3.js-powered horizontal scrolling carousel with mousewheel support
 */

import { formatDate, formatRuntime } from './main.js';

// Carousel state
let carouselState = {
    currentIndex: 0,
    items: [],
    itemWidth: 280,
    gap: 24,
    isScrolling: false,
    container: null,
};

/**
 * Initialize carousel
 */
export function initCarousel() {
    console.log('🎠 Initializing D3.js carousel...');

    // Listen for data ready event
    window.addEventListener('carouselDataReady', (event) => {
        const { media } = event.detail;
        renderCarousel(media);
    });

    // Setup mousewheel listener
    setupMousewheelScroll();
}

/**
 * Render carousel with D3.js
 *
 * @param {Array} items - Media items to display
 */
function renderCarousel(items) {
    if (!items || items.length === 0) {
        showEmptyState();
        return;
    }

    carouselState.items = items;
    carouselState.currentIndex = 0;

    const container = d3.select('#media-carousel');
    container.html(''); // Clear previous content

    // Create carousel structure with simple HTML
    const carouselWrapper = container
        .append('div')
        .attr('class', 'carousel-wrapper')
        .style('display', 'flex')
        .style('gap', '24px')
        .style('padding', '40px')
        .style('justify-content', 'center')
        .style('flex-wrap', 'wrap');

    carouselState.container = container;

    // Render items as HTML divs
    const itemDivs = carouselWrapper
        .selectAll('.carousel-item')
        .data(items, d => d.id)
        .enter()
        .append('div')
        .attr('class', 'carousel-item')
        .attr('data-media-id', d => d.id)
        .style('width', '280px')
        .style('cursor', 'pointer')
        .style('opacity', 0);

    // Animate entrance
    itemDivs
        .transition()
        .duration(300)
        .delay((d, i) => i * 50)
        .style('opacity', 1);

    // Build each item
    itemDivs.each(function(d) {
        const item = d3.select(this);

        // Poster wrapper
        const posterWrapper = item.append('div')
            .attr('class', 'media-poster-wrapper');

        if (d.poster_path) {
            posterWrapper.append('img')
                .attr('class', 'media-poster')
                .attr('src', getTMDBImageURL(d.poster_path, 'w500'))
                .attr('alt', d.title)
                .on('error', function() {
                    d3.select(this.parentNode)
                        .html(`<div class="media-poster loading" style="height: 420px; display: flex; align-items: center; justify-content: center; background: #2a2a3e;">${d.title}</div>`);
                });
        } else {
            posterWrapper.html(`<div class="media-poster loading" style="height: 420px; display: flex; align-items: center; justify-content: center; background: #2a2a3e;">${d.title}</div>`);
        }

        // Media info
        const infoDiv = item.append('div')
            .attr('class', 'media-info')
            .style('padding', '16px');

        infoDiv.append('h3')
            .attr('class', 'media-title')
            .style('margin', '0 0 8px 0')
            .style('font-size', '18px')
            .text(d.title);

        // Meta information
        const metaDiv = infoDiv.append('div')
            .attr('class', 'media-meta')
            .style('display', 'flex')
            .style('gap', '12px')
            .style('flex-wrap', 'wrap')
            .style('font-size', '14px')
            .style('color', '#a0a0b0');

        if (d.release_date) {
            const year = new Date(d.release_date).getFullYear();
            metaDiv.append('span')
                .attr('class', 'media-year')
                .text(year);
        }

        if (d.runtime) {
            metaDiv.append('span')
                .attr('class', 'media-runtime')
                .text(formatRuntime(d.runtime));
        }

        if (d.tmdb_rating) {
            const ratingSpan = metaDiv.append('span')
                .attr('class', 'media-rating');

            ratingSpan.append('span')
                .html('⭐ ');

            ratingSpan.append('span')
                .text(parseFloat(d.tmdb_rating).toFixed(1));
        }

        // Genres
        if (d.genres && d.genres.length > 0) {
            const genresDiv = infoDiv.append('div')
                .attr('class', 'media-genres')
                .style('display', 'flex')
                .style('gap', '8px')
                .style('margin-top', '8px')
                .style('flex-wrap', 'wrap');

            d.genres.slice(0, 3).forEach(genre => {
                genresDiv.append('span')
                    .attr('class', 'genre-tag')
                    .style('padding', '4px 12px')
                    .style('background', '#3a3a5e')
                    .style('border-radius', '12px')
                    .style('font-size', '12px')
                    .text(typeof genre === 'string' ? genre : genre.name);
            });
        }
    });

    console.log(`✅ Carousel rendered with ${items.length} items`);
}

/**
 * Setup mousewheel scrolling
 */
function setupMousewheelScroll() {
    const container = document.getElementById('media-carousel');
    if (!container) return;

    let scrollTimeout;

    container.addEventListener('wheel', (event) => {
        // Allow natural scrolling if content overflows
        // This is mainly for future when we have many items
    }, { passive: true });
}

/**
 * Show empty state
 */
function showEmptyState() {
    const container = d3.select('#media-carousel');
    container.html('<p class="empty-message">No media available. Try changing your filters.</p>');
}

/**
 * Get TMDB image URL
 *
 * @param {string} path - Image path from TMDB
 * @param {string} size - Image size (w92, w154, w185, w342, w500, w780, original)
 * @returns {string} - Full image URL
 */
function getTMDBImageURL(path, size = 'w500') {
    if (!path) return '';
    // TMDB image base URL
    const baseURL = 'https://image.tmdb.org/t/p';
    return `${baseURL}/${size}${path}`;
}

// Initialize carousel when module loads
initCarousel();

// Export functions for external use
export { renderCarousel };
