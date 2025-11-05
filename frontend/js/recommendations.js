/**
 * Recommendations UI Module.
 *
 * Handles recommendation generation, preset selection, and results display.
 */

import * as API from './api-client.js';

// State
let currentPresets = [];
let currentRecommendations = [];
let selectedPresetId = null;

/**
 * Initialize recommendations module.
 */
export async function init() {
    console.log('Initializing recommendations module...');

    // Load presets
    await loadPresets();

    // Setup event listeners
    setupEventListeners();

    console.log('Recommendations module initialized');
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
}

/**
 * Load and populate criteria presets.
 */
async function loadPresets() {
    try {
        currentPresets = await API.getCriteriaPresets();

        const presetSelect = document.getElementById('criteria-preset');
        if (!presetSelect) return;

        // Clear existing options
        presetSelect.innerHTML = '<option value="">Select Criteria Preset...</option>';

        // Add presets
        currentPresets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset.id;
            option.textContent = preset.name;
            if (preset.is_default) {
                option.textContent += ' ⭐';
            }
            presetSelect.appendChild(option);
        });

        console.log(`Loaded ${currentPresets.length} presets`);
    } catch (error) {
        console.error('Failed to load presets:', error);
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

    selectedPresetId = presetId;

    // Find preset
    const preset = currentPresets.find(p => p.id === presetId);
    if (!preset) return;

    // Show preset info
    showPresetInfo(preset);

    // Generate recommendations
    await generateRecommendations(presetId);
}

/**
 * Generate recommendations using a preset.
 *
 * @param {string} presetId - Preset UUID
 */
async function generateRecommendations(presetId) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    // Show loading state
    container.innerHTML = '<div class="loading-message">Generating recommendations...</div>';

    try {
        const response = await API.getRecommendations({
            preset_id: presetId,
            limit: 10
        });

        currentRecommendations = response.recommendations;

        // Display recommendations
        displayRecommendations(response);

    } catch (error) {
        console.error('Failed to generate recommendations:', error);
        container.innerHTML = '<div class="error-message">Failed to generate recommendations. Please try again.</div>';
    }
}

/**
 * Display recommendations in the UI.
 *
 * @param {Object} response - Recommendation response
 */
function displayRecommendations(response) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    if (response.recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-message">
                <p>No media found matching these criteria.</p>
                <p>Try adjusting your criteria or selecting a different preset.</p>
            </div>
        `;
        return;
    }

    // Create header with stats
    const header = document.createElement('div');
    header.className = 'recommendations-header';
    header.innerHTML = `
        <div class="recommendations-stats">
            <span class="stat-item">
                <strong>${response.recommendations.length}</strong> recommendations
            </span>
            <span class="stat-item">
                from <strong>${response.total_candidates}</strong> candidates
            </span>
            <span class="stat-item">
                in <strong>${response.execution_time_ms.toFixed(1)}</strong>ms
            </span>
        </div>
        ${response.preset_name ? `<div class="preset-name">Using: <strong>${response.preset_name}</strong></div>` : ''}
    `;

    // Create recommendations grid
    const grid = document.createElement('div');
    grid.className = 'recommendations-grid';

    response.recommendations.forEach((item, index) => {
        const card = createRecommendationCard(item, index + 1);
        grid.appendChild(card);
    });

    // Clear and populate container
    container.innerHTML = '';
    container.appendChild(header);
    container.appendChild(grid);
}

/**
 * Create a recommendation card.
 *
 * @param {Object} item - Scored media item
 * @param {number} rank - Ranking position
 * @returns {HTMLElement} - Card element
 */
function createRecommendationCard(item, rank) {
    const { media, score, score_breakdown, matched_criteria } = item;

    const card = document.createElement('div');
    card.className = 'recommendation-card';

    // Score percentage
    const scorePercent = (score * 100).toFixed(1);

    // Score color based on value
    let scoreClass = 'score-low';
    if (score >= 0.7) scoreClass = 'score-high';
    else if (score >= 0.5) scoreClass = 'score-medium';

    card.innerHTML = `
        <div class="card-rank">#${rank}</div>
        <div class="card-score ${scoreClass}">${scorePercent}%</div>
        <div class="card-content">
            <h3 class="card-title">${media.title}</h3>
            ${media.release_date ? `<div class="card-year">${new Date(media.release_date).getFullYear()}</div>` : ''}
            ${media.overview ? `<p class="card-overview">${truncate(media.overview, 150)}</p>` : ''}
            <div class="card-meta">
                ${media.runtime ? `<span class="meta-item">${media.runtime} min</span>` : ''}
                ${media.tmdb_rating ? `<span class="meta-item">⭐ ${media.tmdb_rating}</span>` : ''}
                ${media.maturity_rating ? `<span class="meta-item">${media.maturity_rating}</span>` : ''}
            </div>
            <div class="card-score-breakdown">
                <strong>Score Breakdown:</strong>
                <div class="breakdown-items">
                    ${Object.entries(score_breakdown).map(([criterion, criterionScore]) => `
                        <div class="breakdown-item">
                            <span class="criterion-name">${formatCriterionName(criterion)}</span>
                            <span class="criterion-score">${(criterionScore * 100).toFixed(0)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ${matched_criteria.length > 0 ? `
                <div class="card-matched">
                    <strong>Matched:</strong> ${matched_criteria.map(c => formatCriterionName(c)).join(', ')}
                </div>
            ` : ''}
        </div>
    `;

    // Click to view details
    card.addEventListener('click', () => {
        showMediaDetails(media);
    });

    return card;
}

/**
 * Show preset information.
 *
 * @param {Object} preset - Preset object
 */
function showPresetInfo(preset) {
    // Could display preset info in a sidebar or tooltip
    console.log('Selected preset:', preset.name, preset.description);
}

/**
 * Open criteria builder for custom criteria.
 */
function openCriteriaBuilder() {
    console.log('Opening criteria builder...');
    // This will be implemented in criteria-builder.js
    const event = new CustomEvent('open-criteria-builder');
    document.dispatchEvent(event);
}

/**
 * Clear recommendations display.
 */
function clearRecommendations() {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    container.innerHTML = '<p class="empty-message">Select a criteria preset or create your own to get recommendations.</p>';
}

/**
 * Show media details modal.
 *
 * @param {Object} media - Media object
 */
function showMediaDetails(media) {
    // Create a simple modal or navigate to details page
    console.log('Show details for:', media.title);
    // TODO: Implement modal or details view
    alert(`Details for: ${media.title}\n\n${media.overview || 'No overview available.'}`);
}

/**
 * Show error message.
 *
 * @param {string} message - Error message
 */
function showError(message) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    container.innerHTML = `<div class="error-message">${message}</div>`;
}

/**
 * Truncate text to a maximum length.
 *
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
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
