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
    scrollTimeout: null,
    currentlyViewedItem: null,
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
    console.log('🎠 renderCarousel called with', items ? items.length : 0, 'items');

    if (!items || items.length === 0) {
        showEmptyState();
        return;
    }

    carouselState.items = items;
    carouselState.currentIndex = 0;

    const container = d3.select('#media-carousel');
    console.log('📦 Container element:', container.node());
    console.log('📋 Container HTML before cleanup:', container.node() ? container.node().innerHTML.substring(0, 200) : 'NULL');

    // Remove only the carousel wrapper, preserve the count badge
    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.empty-message').remove();
    container.selectAll('.loading-message').remove();

    console.log('📋 Container HTML after cleanup:', container.node() ? container.node().innerHTML.substring(0, 200) : 'NULL');

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
        .style('-webkit-overflow-scrolling', 'touch') // Smooth scrolling on mobile
        .style('scrollbar-width', 'thin') // Firefox
        .style('scrollbar-color', '#6366f1 #2a2a3e'); // Firefox

    carouselState.container = container;

    // Render items as HTML divs
    const itemDivs = carouselWrapper
        .selectAll('.carousel-item')
        .data(items, d => d.id)
        .enter()
        .append('div')
        .attr('class', 'carousel-item')
        .attr('data-media-id', d => d.id)
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

    // Update carousel count
    updateCarouselCount(items.length);

    console.log(`✅ Carousel rendered with ${items.length} items`);
}

/**
 * Update carousel count badge
 *
 * @param {number} count - Number of items
 */
function updateCarouselCount(count) {
    const countElement = document.getElementById('carousel-count');
    console.log('🔢 updateCarouselCount called with count:', count);
    console.log('🎯 Count element found:', countElement);
    console.log('📍 Count element HTML:', countElement ? countElement.outerHTML : 'NULL');

    if (countElement) {
        countElement.textContent = count;
        console.log('✅ Count updated to:', count);
    } else {
        console.error('❌ carousel-count element not found in DOM!');
    }
}

/**
 * Setup mousewheel scrolling
 */
function setupMousewheelScroll() {
    const container = document.getElementById('media-carousel');
    if (!container) return;

    container.addEventListener('wheel', (event) => {
        // Find the carousel wrapper inside the container
        const wrapper = container.querySelector('.carousel-wrapper');
        if (!wrapper) return;

        // Convert vertical scroll to horizontal scroll
        if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
            event.preventDefault();
            wrapper.scrollLeft += event.deltaY;
        }
    }, { passive: false });

    // Setup scroll tracking for sidebar updates
    setupScrollTracking();
}

/**
 * Setup scroll tracking to detect which item is in view
 */
function setupScrollTracking() {
    const container = document.getElementById('media-carousel');
    if (!container) return;

    // Debounced scroll handler
    container.addEventListener('scroll', () => {
        const wrapper = container.querySelector('.carousel-wrapper');
        if (!wrapper) return;

        // Clear existing timeout
        if (carouselState.scrollTimeout) {
            clearTimeout(carouselState.scrollTimeout);
        }

        // Debounce to avoid too many updates
        carouselState.scrollTimeout = setTimeout(() => {
            detectCenterItem();
        }, 150);
    }, true);
}

/**
 * Detect which carousel item is currently centered in view
 */
function detectCenterItem() {
    const wrapper = document.querySelector('.carousel-wrapper');
    if (!wrapper) return;

    const items = wrapper.querySelectorAll('.carousel-item');
    if (items.length === 0) return;

    const wrapperRect = wrapper.getBoundingClientRect();
    const centerX = wrapperRect.left + wrapperRect.width / 2;

    let closestItem = null;
    let closestDistance = Infinity;

    items.forEach(item => {
        const itemRect = item.getBoundingClientRect();
        const itemCenterX = itemRect.left + itemRect.width / 2;
        const distance = Math.abs(centerX - itemCenterX);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestItem = item;
        }
    });

    if (closestItem) {
        const mediaId = closestItem.dataset.mediaId;

        // Only update if this is a different item
        if (carouselState.currentlyViewedItem !== mediaId) {
            carouselState.currentlyViewedItem = mediaId;

            // Dispatch event for sidebar to listen to
            window.dispatchEvent(new CustomEvent('carouselItemInView', {
                detail: { mediaId }
            }));
        }
    }
}

/**
 * Show empty state
 */
function showEmptyState() {
    const container = d3.select('#media-carousel');

    // Remove previous content but preserve count badge
    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.empty-message').remove();
    container.selectAll('.loading-message').remove();

    // Add empty message
    container.append('p')
        .attr('class', 'empty-message')
        .text('No media available. Try changing your filters.');

    // Update count to 0
    updateCarouselCount(0);
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
export { renderCarousel, detectCenterItem };
