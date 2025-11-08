/**
 * Recommendations UI Module.
 *
 * Handles recommendation generation, preset selection, and carousel display.
 */

import * as API from './api-client.js';

// State
let recommendationState = {
    currentPresets: [],
    currentRecommendations: [],
    selectedPresetId: null,
    currentIndex: 0,
    currentlyViewedItem: null,
    scrollTimeout: null
};

/**
 * Initialize recommendations module.
 */
export async function init() {
    console.log('🎯 Initializing recommendations module...');

    // Load presets
    await loadPresets();

    // Setup event listeners
    setupEventListeners();

    console.log('✅ Recommendations module initialized');
}

/**
 * Setup event listeners for recommendations view.
 */
function setupEventListeners() {
    // Preset selection
    const presetSelect = document.getElementById('criteria-preset');
    if (presetSelect) {
        presetSelect.addEventListener('change', handlePresetChange);
    }

    // Create custom criteria button
    const createButton = document.getElementById('create-criteria');
    if (createButton) {
        createButton.addEventListener('click', openCriteriaBuilder);
    }

    // Listen for carousel item scroll events
    window.addEventListener('recommendationItemInView', (event) => {
        const { index } = event.detail;
        renderRecommendationDetail(index);
    });
}

/**
 * Load and populate criteria presets.
 */
async function loadPresets() {
    try {
        recommendationState.currentPresets = await API.getCriteriaPresets();

        const presetSelect = document.getElementById('criteria-preset');
        if (!presetSelect) return;

        // Clear existing options
        presetSelect.innerHTML = '';

        // Add presets
        recommendationState.currentPresets.forEach((preset, index) => {
            const option = document.createElement('option');
            option.value = preset.id;
            option.textContent = preset.name;
            if (preset.is_default) {
                option.textContent += ' ⭐';
            }
            presetSelect.appendChild(option);
        });

        console.log(`📋 Loaded ${recommendationState.currentPresets.length} presets`);

        // Auto-select first preset and generate recommendations
        if (recommendationState.currentPresets.length > 0) {
            const firstPreset = recommendationState.currentPresets[0];
            presetSelect.value = firstPreset.id;
            recommendationState.selectedPresetId = firstPreset.id;

            // Generate recommendations for the first preset
            await generateRecommendations(firstPreset.id, firstPreset);
        }
    } catch (error) {
        console.error('❌ Failed to load presets:', error);
        showError('Failed to load recommendation presets');
    }
}

/**
 * Handle preset selection change.
 *
 * @param {Event} event - Change event
 */
async function handlePresetChange(event) {
    const presetId = event.target.value;

    if (!presetId) {
        // Clear recommendations
        clearRecommendations();
        return;
    }

    recommendationState.selectedPresetId = presetId;

    // Find preset
    const preset = recommendationState.currentPresets.find(p => p.id === presetId);
    if (!preset) return;

    // Generate recommendations
    await generateRecommendations(presetId, preset);
}

/**
 * Generate recommendations using a preset.
 *
 * @param {string} presetId - Preset UUID
 * @param {Object} preset - Preset object
 */
async function generateRecommendations(presetId, preset) {
    const container = d3.select('#recommendations-carousel');
    if (!container.node()) return;

    // Show loading state
    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.empty-message').remove();
    container.append('div')
        .attr('class', 'loading-message')
        .text('Generating recommendations...');

    // Show preset info in sidebar
    showPresetInfo(preset);

    try {
        const response = await API.getRecommendations({
            preset_id: presetId,
            limit: 20
        });

        recommendationState.currentRecommendations = response.recommendations;

        // Display recommendations in carousel
        renderRecommendationsCarousel(response);

    } catch (error) {
        console.error('❌ Failed to generate recommendations:', error);
        container.selectAll('.loading-message').remove();
        container.append('div')
            .attr('class', 'error-message')
            .text('Failed to generate recommendations. Please try again.');
    }
}

/**
 * Render recommendations carousel with D3.js.
 *
 * @param {Object} response - Recommendation response
 */
function renderRecommendationsCarousel(response) {
    console.log('🎠 Rendering recommendations carousel with', response.recommendations.length, 'items');

    const container = d3.select('#recommendations-carousel');
    if (!container.node()) return;

    if (response.recommendations.length === 0) {
        container.selectAll('.loading-message').remove();
        container.selectAll('.carousel-wrapper').remove();
        container.append('p')
            .attr('class', 'empty-message')
            .text('No media found matching these criteria. Try adjusting your criteria or selecting a different preset.');
        updateRecommendationsCount(0);
        return;
    }

    // Remove loading/empty messages
    container.selectAll('.loading-message').remove();
    container.selectAll('.empty-message').remove();
    container.selectAll('.carousel-wrapper').remove();

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
        .data(response.recommendations, (d, i) => i)
        .enter()
        .append('div')
        .attr('class', 'carousel-item recommendation-item')
        .attr('data-index', (d, i) => i)
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
    itemDivs.each(function(item, index) {
        const itemDiv = d3.select(this);
        const { media, score } = item;

        // Rank badge
        itemDiv.append('div')
            .attr('class', 'recommendation-rank')
            .style('position', 'absolute')
            .style('top', '8px')
            .style('left', '8px')
            .style('background', 'rgba(99, 102, 241, 0.9)')
            .style('color', 'white')
            .style('padding', '4px 12px')
            .style('border-radius', '12px')
            .style('font-weight', 'bold')
            .style('font-size', '14px')
            .style('z-index', '10')
            .text(`#${index + 1}`);

        // Score badge
        const scorePercent = (score * 100).toFixed(0);
        let scoreColor = '#ef4444'; // Low score - red
        if (score >= 0.7) scoreColor = '#10b981'; // High score - green
        else if (score >= 0.5) scoreColor = '#f59e0b'; // Medium score - orange

        itemDiv.append('div')
            .attr('class', 'recommendation-score')
            .style('position', 'absolute')
            .style('top', '8px')
            .style('right', '8px')
            .style('background', scoreColor)
            .style('color', 'white')
            .style('padding', '6px 12px')
            .style('border-radius', '12px')
            .style('font-weight', 'bold')
            .style('font-size', '16px')
            .style('z-index', '10')
            .text(`${scorePercent}%`);

        // Poster wrapper
        const posterWrapper = itemDiv.append('div')
            .attr('class', 'media-poster-wrapper');

        if (media.poster_path) {
            const img = posterWrapper.append('img')
                .attr('class', 'media-poster')
                .attr('src', getTMDBImageURL(media.poster_path, 'w500'))
                .attr('alt', media.title)
                .attr('draggable', true)
                .attr('data-media-id', media.id)
                .attr('data-media-title', media.title);

            // Add dragstart event listener
            img.on('dragstart', function(event) {
                console.log('🎬 DRAG START - Movie:', media.title, 'ID:', media.id);
                event.dataTransfer.setData('mediaId', media.id);
                event.dataTransfer.setData('mediaTitle', media.title);
                event.dataTransfer.effectAllowed = 'copy';
            });

            img.on('drag', function(event) {
                console.log('🎬 DRAGGING...');
            });

            img.on('dragend', function(event) {
                console.log('🎬 DRAG END');
            });

            img.on('error', function() {
                d3.select(this.parentNode)
                    .html(`<div class="media-poster loading" style="height: 420px; display: flex; align-items: center; justify-content: center; background: #2a2a3e;">${media.title}</div>`);
            });
        } else {
            posterWrapper.html(`<div class="media-poster loading" style="height: 420px; display: flex; align-items: center; justify-content: center; background: #2a2a3e;">${media.title}</div>`);
        }

        // Media info
        const infoDiv = itemDiv.append('div')
            .attr('class', 'media-info')
            .style('padding', '16px');

        infoDiv.append('h3')
            .attr('class', 'media-title')
            .style('margin', '0 0 8px 0')
            .style('font-size', '18px')
            .text(media.title);

        // Meta information
        const metaDiv = infoDiv.append('div')
            .attr('class', 'media-meta')
            .style('display', 'flex')
            .style('gap', '12px')
            .style('flex-wrap', 'wrap')
            .style('font-size', '14px')
            .style('color', '#a0a0b0');

        if (media.release_date) {
            const year = new Date(media.release_date).getFullYear();
            metaDiv.append('span')
                .attr('class', 'media-year')
                .text(year);
        }

        if (media.runtime) {
            metaDiv.append('span')
                .attr('class', 'media-runtime')
                .text(formatRuntime(media.runtime));
        }

        if (media.tmdb_rating) {
            const ratingSpan = metaDiv.append('span')
                .attr('class', 'media-rating');

            ratingSpan.append('span')
                .html('⭐ ');

            ratingSpan.append('span')
                .text(parseFloat(media.tmdb_rating).toFixed(1));
        }

        // Genres
        if (media.genres && media.genres.length > 0) {
            const genresDiv = infoDiv.append('div')
                .attr('class', 'media-genres')
                .style('display', 'flex')
                .style('gap', '8px')
                .style('margin-top', '8px')
                .style('flex-wrap', 'wrap');

            media.genres.slice(0, 3).forEach(genre => {
                genresDiv.append('span')
                    .attr('class', 'genre-tag')
                    .style('padding', '4px 12px')
                    .style('background', '#3a3a5e')
                    .style('border-radius', '12px')
                    .style('font-size', '12px')
                    .text(typeof genre === 'string' ? genre : genre.name);
            });
        }

        // Click handler
        itemDiv.on('click', () => {
            renderRecommendationDetail(index);
        });
    });

    // Update count
    updateRecommendationsCount(response.recommendations.length);

    // Setup mousewheel scrolling (needs to be done after carousel is rendered)
    setupMousewheelScroll();

    // Setup scroll tracking
    setupScrollTracking();

    // Show first recommendation details
    if (response.recommendations.length > 0) {
        renderRecommendationDetail(0);
    }

    console.log(`✅ Carousel rendered with ${response.recommendations.length} recommendations`);
}

/**
 * Render recommendation detail card in sidebar.
 *
 * @param {number} index - Index of recommendation
 */
function renderRecommendationDetail(index) {
    if (!recommendationState.currentRecommendations || index >= recommendationState.currentRecommendations.length) {
        return;
    }

    const item = recommendationState.currentRecommendations[index];
    const { media, score, score_breakdown, matched_criteria } = item;

    const container = d3.select('#recommendation-detail-card');
    container.html(''); // Clear

    const scorePercent = (score * 100).toFixed(1);

    // Header with rank and score
    const header = container.append('div')
        .attr('class', 'recommendation-detail-header')
        .style('padding', '20px')
        .style('border-bottom', '1px solid #3a3a5e');

    header.append('div')
        .attr('class', 'recommendation-detail-rank')
        .style('font-size', '14px')
        .style('color', '#a0a0b0')
        .style('margin-bottom', '8px')
        .text(`Recommendation #${index + 1}`);

    header.append('h2')
        .attr('class', 'recommendation-detail-title')
        .style('margin', '0 0 12px 0')
        .style('font-size', '24px')
        .text(media.title);

    // Large score display
    let scoreColor = '#ef4444';
    if (score >= 0.7) scoreColor = '#10b981';
    else if (score >= 0.5) scoreColor = '#f59e0b';

    header.append('div')
        .attr('class', 'recommendation-detail-score')
        .style('font-size', '36px')
        .style('font-weight', 'bold')
        .style('color', scoreColor)
        .text(`${scorePercent}% Match`);

    // Content section
    const content = container.append('div')
        .attr('class', 'recommendation-detail-content')
        .style('padding', '20px');

    // Meta info
    if (media.release_date || media.runtime || media.tmdb_rating) {
        const metaDiv = content.append('div')
            .attr('class', 'recommendation-detail-meta')
            .style('display', 'flex')
            .style('gap', '16px')
            .style('margin-bottom', '16px')
            .style('font-size', '14px')
            .style('color', '#a0a0b0');

        if (media.release_date) {
            metaDiv.append('span').text(new Date(media.release_date).getFullYear());
        }
        if (media.runtime) {
            metaDiv.append('span').text(formatRuntime(media.runtime));
        }
        if (media.tmdb_rating) {
            metaDiv.append('span').html(`⭐ ${parseFloat(media.tmdb_rating).toFixed(1)}`);
        }
    }

    // Overview
    if (media.overview) {
        content.append('p')
            .attr('class', 'recommendation-detail-overview')
            .style('margin-bottom', '20px')
            .style('line-height', '1.6')
            .text(media.overview);
    }

    // Score breakdown
    if (score_breakdown && Object.keys(score_breakdown).length > 0) {
        content.append('h3')
            .style('margin', '20px 0 12px 0')
            .style('font-size', '18px')
            .text('Score Breakdown');

        const breakdownDiv = content.append('div')
            .attr('class', 'score-breakdown-list')
            .style('display', 'flex')
            .style('flex-direction', 'column')
            .style('gap', '8px');

        Object.entries(score_breakdown).forEach(([criterion, criterionScore]) => {
            const item = breakdownDiv.append('div')
                .attr('class', 'breakdown-item')
                .style('display', 'flex')
                .style('justify-content', 'space-between')
                .style('align-items', 'center')
                .style('padding', '8px 12px')
                .style('background', '#2a2a3e')
                .style('border-radius', '8px');

            item.append('span')
                .attr('class', 'criterion-name')
                .style('flex', '1')
                .text(formatCriterionName(criterion));

            item.append('span')
                .attr('class', 'criterion-score')
                .style('font-weight', 'bold')
                .style('color', criterionScore >= 0.7 ? '#10b981' : '#f59e0b')
                .text(`${(criterionScore * 100).toFixed(0)}%`);
        });
    }

    // Matched criteria
    if (matched_criteria && matched_criteria.length > 0) {
        content.append('h3')
            .style('margin', '20px 0 12px 0')
            .style('font-size', '18px')
            .text('Matched Criteria');

        const matchedDiv = content.append('div')
            .attr('class', 'matched-criteria-list')
            .style('display', 'flex')
            .style('flex-wrap', 'wrap')
            .style('gap', '8px');

        matched_criteria.forEach(criterion => {
            matchedDiv.append('span')
                .attr('class', 'matched-tag')
                .style('padding', '6px 12px')
                .style('background', '#10b981')
                .style('color', 'white')
                .style('border-radius', '12px')
                .style('font-size', '13px')
                .text(formatCriterionName(criterion));
        });
    }

    // Genres
    if (media.genres && media.genres.length > 0) {
        content.append('h3')
            .style('margin', '20px 0 12px 0')
            .style('font-size', '18px')
            .text('Genres');

        const genresDiv = content.append('div')
            .attr('class', 'genres-list')
            .style('display', 'flex')
            .style('flex-wrap', 'wrap')
            .style('gap', '8px');

        media.genres.forEach(genre => {
            genresDiv.append('span')
                .attr('class', 'genre-tag')
                .style('padding', '6px 12px')
                .style('background', '#3a3a5e')
                .style('border-radius', '12px')
                .style('font-size', '13px')
                .text(typeof genre === 'string' ? genre : genre.name);
        });
    }

    console.log(`📄 Rendered detail card for: ${media.title}`);
}

/**
 * Show preset information in sidebar.
 *
 * @param {Object} preset - Preset object
 */
function showPresetInfo(preset) {
    const container = d3.select('#recommendation-detail-card');
    container.html('');

    const content = container.append('div')
        .attr('class', 'preset-info')
        .style('padding', '20px');

    content.append('h2')
        .style('margin', '0 0 12px 0')
        .style('font-size', '24px')
        .text(preset.name);

    if (preset.description) {
        content.append('p')
            .style('color', '#a0a0b0')
            .style('line-height', '1.6')
            .text(preset.description);
    }

    content.append('div')
        .attr('class', 'loading-message')
        .style('margin-top', '20px')
        .text('Generating recommendations...');
}

/**
 * Update recommendations count badge.
 *
 * @param {number} count - Number of recommendations
 */
function updateRecommendationsCount(count) {
    const countElement = document.getElementById('recommendations-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

/**
 * Setup mousewheel scrolling for carousel.
 */
function setupMousewheelScroll() {
    const container = document.getElementById('recommendations-carousel');
    if (!container) return;

    container.addEventListener('wheel', (event) => {
        const wrapper = container.querySelector('.carousel-wrapper');
        if (!wrapper) return;

        // Convert vertical scroll to horizontal scroll with 3x speed
        if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
            event.preventDefault();
            wrapper.scrollLeft += event.deltaY * 3;
        }
    }, { passive: false });
}

/**
 * Setup scroll tracking to detect which item is in view.
 */
function setupScrollTracking() {
    const container = document.getElementById('recommendations-carousel');
    if (!container) return;

    // Debounced scroll handler
    container.addEventListener('scroll', () => {
        const wrapper = container.querySelector('.carousel-wrapper');
        if (!wrapper) return;

        // Clear existing timeout
        if (recommendationState.scrollTimeout) {
            clearTimeout(recommendationState.scrollTimeout);
        }

        // Debounce to avoid too many updates
        recommendationState.scrollTimeout = setTimeout(() => {
            detectCenterItem();
        }, 150);
    }, true);
}

/**
 * Detect which carousel item is currently centered in view.
 */
function detectCenterItem() {
    const wrapper = document.querySelector('#recommendations-carousel .carousel-wrapper');
    if (!wrapper) return;

    const items = wrapper.querySelectorAll('.recommendation-item');
    if (items.length === 0) return;

    const wrapperRect = wrapper.getBoundingClientRect();
    const centerX = wrapperRect.left + wrapperRect.width / 2;

    let closestItem = null;
    let closestDistance = Infinity;
    let closestIndex = 0;

    items.forEach((item, index) => {
        const itemRect = item.getBoundingClientRect();
        const itemCenterX = itemRect.left + itemRect.width / 2;
        const distance = Math.abs(centerX - itemCenterX);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestItem = item;
            closestIndex = index;
        }
    });

    if (closestItem) {
        const index = parseInt(closestItem.dataset.index);

        // Only update if this is a different item
        if (recommendationState.currentlyViewedItem !== index) {
            recommendationState.currentlyViewedItem = index;

            // Dispatch event
            window.dispatchEvent(new CustomEvent('recommendationItemInView', {
                detail: { index }
            }));
        }
    }
}

/**
 * Open criteria builder for custom criteria.
 */
function openCriteriaBuilder() {
    console.log('📝 Opening criteria builder...');
    const event = new CustomEvent('open-criteria-builder');
    document.dispatchEvent(event);
}

/**
 * Clear recommendations display.
 */
function clearRecommendations() {
    const container = d3.select('#recommendations-carousel');
    if (!container.node()) return;

    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.loading-message').remove();
    container.append('p')
        .attr('class', 'empty-message')
        .text('Select a criteria preset or create your own to get recommendations.');

    updateRecommendationsCount(0);

    // Clear sidebar
    const sidebar = d3.select('#recommendation-detail-card');
    sidebar.html('');
    sidebar.append('p')
        .attr('class', 'empty-message')
        .text('Select a criteria preset to get started');
}

/**
 * Show error message.
 *
 * @param {string} message - Error message
 */
function showError(message) {
    const container = d3.select('#recommendations-carousel');
    if (!container.node()) return;

    container.selectAll('.carousel-wrapper').remove();
    container.selectAll('.loading-message').remove();
    container.append('div')
        .attr('class', 'error-message')
        .text(message);
}

/**
 * Format criterion name for display.
 *
 * @param {string} criterion - Criterion field name
 * @returns {string} - Formatted name
 */
function formatCriterionName(criterion) {
    return criterion
        .replace(/_/g, ' ')
        .replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Format runtime (minutes to hours and minutes).
 *
 * @param {number} runtime - Runtime in minutes
 * @returns {string} - Formatted runtime
 */
function formatRuntime(runtime) {
    const hours = Math.floor(runtime / 60);
    const minutes = runtime % 60;
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

/**
 * Get TMDB image URL.
 *
 * @param {string} path - Image path from TMDB
 * @param {string} size - Image size (w92, w154, w185, w342, w500, w780, original)
 * @returns {string} - Full image URL
 */
function getTMDBImageURL(path, size = 'w500') {
    if (!path) return '';
    const baseURL = 'https://image.tmdb.org/t/p';
    return `${baseURL}/${size}${path}`;
}
