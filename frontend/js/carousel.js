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
    svg: null,
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

    // Create carousel structure
    const carouselWrapper = container
        .append('div')
        .attr('class', 'carousel-viewport');

    // Calculate total width needed to show all items
    const itemWidth = carouselState.itemWidth;
    const gap = carouselState.gap;
    const totalItemsWidth = items.length * itemWidth + (items.length - 1) * gap;
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = 600;

    // Use the larger of container width or total items width
    const svgWidth = Math.max(containerWidth, totalItemsWidth + 100); // Add padding

    const svg = carouselWrapper
        .append('svg')
        .attr('width', '100%')
        .attr('height', containerHeight)
        .attr('viewBox', `0 0 ${svgWidth} ${containerHeight}`)
        .attr('class', 'carousel-svg');

    carouselState.svg = svg;
    carouselState.container = container;

    // Create group for items - center all items together
    const startX = Math.max(50, (containerWidth - totalItemsWidth) / 2);
    const itemsGroup = svg
        .append('g')
        .attr('class', 'carousel-items-group')
        .attr('transform', `translate(${startX}, 40)`);

    // Render items
    renderItems(itemsGroup, items);

    // Add navigation buttons (optional - for scrolling between items)
    if (items.length > 3) {
        addNavigationButtons(container);
    }

    // Add thumbnail strip (optional - for many items)
    if (items.length > 5) {
        addThumbnailStrip(container, items);
    }

    console.log(`✅ Carousel rendered with ${items.length} items`);
}

/**
 * Render carousel items with D3
 *
 * @param {Object} group - D3 selection group
 * @param {Array} items - Media items
 */
function renderItems(group, items) {
    const itemWidth = carouselState.itemWidth;
    const gap = carouselState.gap;

    // Bind data
    const itemGroups = group
        .selectAll('.carousel-item-group')
        .data(items, d => d.id)
        .enter()
        .append('g')
        .attr('class', 'carousel-item-group')
        .attr('data-media-id', d => d.id)
        .attr('transform', (d, i) => {
            const x = i * (itemWidth + gap);
            return `translate(${x}, 0)`;
        })
        .style('opacity', 0);

    // Animate entrance
    itemGroups
        .transition()
        .duration(300)
        .delay((d, i) => i * 50)
        .style('opacity', 1);

    // Create foreign object for HTML content
    const foreignObjects = itemGroups
        .append('foreignObject')
        .attr('width', itemWidth)
        .attr('height', 500)
        .attr('class', 'carousel-item-wrapper');

    // Add HTML content using foreignObject
    foreignObjects.each(function(d, i) {
        const fo = d3.select(this);
        const div = fo.append('xhtml:div')
            .attr('class', `carousel-item ${i === 0 ? 'active' : ''}`)
            .attr('data-media-id', d.id)
            .style('cursor', 'pointer');

        // Poster image
        const posterDiv = div.append('div')
            .attr('class', 'media-poster-wrapper');

        if (d.poster_path) {
            posterDiv.append('img')
                .attr('class', 'media-poster')
                .attr('src', getTMDBImageURL(d.poster_path, 'w500'))
                .attr('alt', d.title)
                .on('error', function() {
                    d3.select(this.parentNode)
                        .html(`<div class="media-poster loading">${d.title}</div>`);
                });
        } else {
            posterDiv.html(`<div class="media-poster loading">${d.title}</div>`);
        }

        // Media info
        const infoDiv = div.append('div')
            .attr('class', 'media-info');

        infoDiv.append('h3')
            .attr('class', 'media-title')
            .text(d.title);

        // Meta information
        const metaDiv = infoDiv.append('div')
            .attr('class', 'media-meta');

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
                .html('⭐');

            ratingSpan.append('span')
                .text(d.tmdb_rating.toFixed(1));
        }

        // Genres
        if (d.genres && d.genres.length > 0) {
            const genresDiv = infoDiv.append('div')
                .attr('class', 'media-genres');

            d.genres.slice(0, 3).forEach(genre => {
                genresDiv.append('span')
                    .attr('class', 'genre-tag')
                    .text(typeof genre === 'string' ? genre : genre.name);
            });
        }
    });

    // Make all items visible (not just first one)
    updateActiveItem(0);
}

/**
 * Setup mousewheel scrolling
 */
function setupMousewheelScroll() {
    const container = document.getElementById('media-carousel');
    if (!container) return;

    let scrollTimeout;

    container.addEventListener('wheel', (event) => {
        // Only handle horizontal scroll
        if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
            event.preventDefault();

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                carouselState.isScrolling = false;
            }, 150);

            if (!carouselState.isScrolling) {
                carouselState.isScrolling = true;

                if (event.deltaY > 0) {
                    // Scroll down = next item
                    scrollToNext();
                } else {
                    // Scroll up = previous item
                    scrollToPrevious();
                }
            }
        }
    }, { passive: false });
}

/**
 * Scroll to next item
 */
function scrollToNext() {
    const maxIndex = carouselState.items.length - 1;
    if (carouselState.currentIndex < maxIndex) {
        carouselState.currentIndex++;
        updateCarouselPosition();
        updateActiveItem(carouselState.currentIndex);
    }
}

/**
 * Scroll to previous item
 */
function scrollToPrevious() {
    if (carouselState.currentIndex > 0) {
        carouselState.currentIndex--;
        updateCarouselPosition();
        updateActiveItem(carouselState.currentIndex);
    }
}

/**
 * Scroll to specific index
 *
 * @param {number} index - Target index
 */
function scrollToIndex(index) {
    if (index >= 0 && index < carouselState.items.length) {
        carouselState.currentIndex = index;
        updateCarouselPosition();
        updateActiveItem(index);
    }
}

/**
 * Update carousel position with animation
 */
function updateCarouselPosition() {
    const itemWidth = carouselState.itemWidth;
    const gap = carouselState.gap;
    const containerWidth = carouselState.container.node().getBoundingClientRect().width;
    const centerOffset = (containerWidth - itemWidth) / 2;

    const targetX = -carouselState.currentIndex * (itemWidth + gap) + centerOffset;

    carouselState.svg
        .select('.carousel-items-group')
        .transition()
        .duration(500)
        .ease(d3.easeCubicOut)
        .attr('transform', `translate(${targetX}, 40)`);

    // Update navigation button states
    updateNavigationButtons();
}

/**
 * Update active item styling
 *
 * @param {number} index - Active item index
 */
function updateActiveItem(index) {
    // Remove active class from all items
    d3.selectAll('.carousel-item')
        .classed('active', false);

    // Add active class to current item
    d3.selectAll('.carousel-item')
        .filter((d, i) => i === index)
        .classed('active', true);

    // Update thumbnail strip
    updateThumbnailActive(index);
}

/**
 * Add navigation buttons
 *
 * @param {Object} container - D3 selection
 */
function addNavigationButtons(container) {
    // Previous button
    const prevButton = container
        .append('div')
        .attr('class', 'carousel-nav prev');

    prevButton
        .append('button')
        .attr('class', 'carousel-nav-button')
        .attr('id', 'carousel-prev')
        .html('←')
        .on('click', scrollToPrevious);

    // Next button
    const nextButton = container
        .append('div')
        .attr('class', 'carousel-nav next');

    nextButton
        .append('button')
        .attr('class', 'carousel-nav-button')
        .attr('id', 'carousel-next')
        .html('→')
        .on('click', scrollToNext);

    updateNavigationButtons();
}

/**
 * Update navigation button states
 */
function updateNavigationButtons() {
    const prevButton = d3.select('#carousel-prev');
    const nextButton = d3.select('#carousel-next');

    // Disable prev if at start
    if (carouselState.currentIndex === 0) {
        prevButton.attr('disabled', true);
    } else {
        prevButton.attr('disabled', null);
    }

    // Disable next if at end
    if (carouselState.currentIndex === carouselState.items.length - 1) {
        nextButton.attr('disabled', true);
    } else {
        nextButton.attr('disabled', null);
    }
}

/**
 * Add thumbnail strip
 *
 * @param {Object} container - D3 selection
 * @param {Array} items - Media items
 */
function addThumbnailStrip(container, items) {
    const thumbnailContainer = container
        .append('div')
        .attr('class', 'carousel-thumbnails');

    const thumbnails = thumbnailContainer
        .selectAll('.carousel-thumbnail')
        .data(items, d => d.id)
        .enter()
        .append('div')
        .attr('class', (d, i) => `carousel-thumbnail ${i === 0 ? 'active' : ''}`)
        .on('click', (event, d) => {
            const index = items.findIndex(item => item.id === d.id);
            scrollToIndex(index);
        });

    thumbnails.each(function(d) {
        const thumb = d3.select(this);

        if (d.poster_path) {
            thumb.append('img')
                .attr('src', getTMDBImageURL(d.poster_path, 'w92'))
                .attr('alt', d.title);
        } else {
            thumb.style('background-color', 'var(--color-surface)')
                .style('display', 'flex')
                .style('align-items', 'center')
                .style('justify-content', 'center')
                .style('font-size', '10px')
                .style('color', 'var(--color-text-muted)')
                .text(d.title.substring(0, 10));
        }
    });
}

/**
 * Update thumbnail active state
 *
 * @param {number} index - Active thumbnail index
 */
function updateThumbnailActive(index) {
    d3.selectAll('.carousel-thumbnail')
        .classed('active', false)
        .filter((d, i) => i === index)
        .classed('active', true);
}

/**
 * Handle item click - Now handled by expanded-card.js via data-media-id
 *
 * @param {Object} item - Media item
 */
function handleItemClick(item) {
    console.log('🎬 Media clicked:', item.title);
    // Expanded card will handle the click via global event delegation
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

/**
 * Handle keyboard navigation
 */
function setupKeyboardNavigation() {
    document.addEventListener('keydown', (event) => {
        // Only handle if carousel view is active
        const carouselView = document.getElementById('carousel-view');
        if (!carouselView || !carouselView.classList.contains('active')) {
            return;
        }

        switch (event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                scrollToPrevious();
                break;
            case 'ArrowRight':
                event.preventDefault();
                scrollToNext();
                break;
            case 'Home':
                event.preventDefault();
                scrollToIndex(0);
                break;
            case 'End':
                event.preventDefault();
                scrollToIndex(carouselState.items.length - 1);
                break;
        }
    });
}

// Initialize carousel when module loads
initCarousel();
setupKeyboardNavigation();

// Export functions for external use
export { renderCarousel, scrollToNext, scrollToPrevious, scrollToIndex };
