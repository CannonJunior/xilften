/**
 * 3D Criteria Visualization
 *
 * Visualizes movies in 3D space based on three criteria:
 * - Storytelling (0-10)
 * - Characters (0-10)
 * - Cohesive Vision (0-10)
 *
 * The cube is oriented so that (10,10,10) points upward.
 *
 * Inspired by: https://codepen.io/meodai/full/zdgXJj/
 */

import * as api from './api-client.js';
import { showExpandedCard } from './expanded-card.js';
import { getPlaceholderPoster } from './placeholder-posters.js';

// Visualization state
const viz3DState = {
    container: null,
    svg: null,
    width: 600,
    height: 600,
    movies: [],
    geometricRankings: [], // Movies sorted by geometric average
    currentMovieIndex: 0, // Current selected movie in rankings
    rotation: { x: 30, y: 45 }, // Rotation angles in degrees
    isDragging: false,
    lastMouse: { x: 0, y: 0 }
};

/**
 * Calculate geometric mean of three values
 */
function geometricMean(a, b, c) {
    return Math.pow(a * b * c, 1/3);
}

/**
 * Get TMDB image URL from path
 */
function getTMDBImageURL(path, size = 'w500', mediaType = 'movie', title = '') {
    if (!path) {
        // Return media-type-specific placeholder
        return getPlaceholderPoster(mediaType, title);
    }
    const baseURL = 'https://image.tmdb.org/t/p';
    return `${baseURL}/${size}${path}`;
}

/**
 * Calculate geometric rankings for all movies
 */
function calculateGeometricRankings() {
    const moviesWithScores = viz3DState.movies.map(movie => {
        const cf = movie.custom_fields;
        const geoMean = geometricMean(
            cf.storytelling,
            cf.characters,
            cf.cohesive_vision
        );
        return {
            ...movie,
            geometricAverage: geoMean
        };
    });

    // Sort by geometric average (descending)
    moviesWithScores.sort((a, b) => b.geometricAverage - a.geometricAverage);

    viz3DState.geometricRankings = moviesWithScores;

    console.log(`📊 Calculated geometric rankings for ${moviesWithScores.length} movies`);
    console.log(`🏆 Top ranked: ${moviesWithScores[0].title} (${moviesWithScores[0].geometricAverage.toFixed(2)})`);
}

/**
 * Initialize 3D visualization
 */
export function init3DVisualization() {
    console.log('🎬 Initializing 3D Criteria Visualization...');

    const container = document.getElementById('criteria-3d-viz');
    if (!container) {
        console.error('❌ 3D visualization container not found');
        return;
    }

    viz3DState.container = container;

    // Create SVG
    createSVG();

    // Setup mouse controls for rotation
    setupMouseControls();

    // Setup mousewheel for movie navigation
    setupMousewheelNavigation();

    // Load and render movies
    loadMovies();

    console.log('✅ 3D Visualization initialized');
}

/**
 * Create SVG container
 */
function createSVG() {
    const container = viz3DState.container;

    // Clear existing content
    container.innerHTML = '';

    // Create SVG
    viz3DState.svg = d3.select(container)
        .append('svg')
        .attr('width', viz3DState.width)
        .attr('height', viz3DState.height)
        .attr('class', 'criteria-3d-svg');

    // Add gradient definitions for depth effect
    const defs = viz3DState.svg.append('defs');

    const gradient = defs.append('linearGradient')
        .attr('id', 'depth-gradient')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '0%')
        .attr('y2', '100%');

    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#6366f1')
        .attr('stop-opacity', 1);

    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#3730a3')
        .attr('stop-opacity', 0.6);
}

/**
 * Setup mouse controls
 */
function setupMouseControls() {
    const svg = viz3DState.svg.node();

    svg.addEventListener('mousedown', (e) => {
        viz3DState.isDragging = true;
        viz3DState.lastMouse = { x: e.clientX, y: e.clientY };
    });

    svg.addEventListener('mousemove', (e) => {
        if (!viz3DState.isDragging) return;

        const deltaX = e.clientX - viz3DState.lastMouse.x;
        const deltaY = e.clientY - viz3DState.lastMouse.y;

        viz3DState.rotation.y += deltaX * 0.5;
        viz3DState.rotation.x -= deltaY * 0.5;

        // Clamp X rotation
        viz3DState.rotation.x = Math.max(-90, Math.min(90, viz3DState.rotation.x));

        viz3DState.lastMouse = { x: e.clientX, y: e.clientY };

        renderMovies();
    });

    svg.addEventListener('mouseup', () => {
        viz3DState.isDragging = false;
    });

    svg.addEventListener('mouseleave', () => {
        viz3DState.isDragging = false;
    });
}

/**
 * Setup mousewheel navigation
 */
function setupMousewheelNavigation() {
    const svg = viz3DState.svg.node();

    svg.addEventListener('wheel', (e) => {
        e.preventDefault();

        // Navigate through rankings
        if (e.deltaY > 0) {
            // Scroll down - next movie
            viz3DState.currentMovieIndex = Math.min(
                viz3DState.currentMovieIndex + 1,
                viz3DState.geometricRankings.length - 1
            );
        } else {
            // Scroll up - previous movie
            viz3DState.currentMovieIndex = Math.max(
                viz3DState.currentMovieIndex - 1,
                0
            );
        }

        selectCurrentMovie();
    }, { passive: false });
}

/**
 * Select and display current movie
 */
async function selectCurrentMovie() {
    if (viz3DState.geometricRankings.length === 0) return;

    const currentMovie = viz3DState.geometricRankings[viz3DState.currentMovieIndex];

    // Show in sidebar
    await showExpandedCard(currentMovie.id);

    // Update poster display
    updatePosterDisplay(currentMovie);

    // Re-render to highlight selected movie
    renderMovies();
}

/**
 * Update poster display in bottom left corner
 */
function updatePosterDisplay(movie) {
    // Remove existing poster container
    const existingPoster = document.getElementById('poster-3d-container');
    if (existingPoster) {
        existingPoster.remove();
    }

    // Ensure container has relative positioning
    viz3DState.container.style.position = 'relative';

    // Create poster container as regular DOM element
    const posterContainer = document.createElement('div');
    posterContainer.id = 'poster-3d-container';
    posterContainer.style.position = 'absolute';
    posterContainer.style.bottom = '20px';
    posterContainer.style.left = '20px';
    posterContainer.style.zIndex = '100';
    posterContainer.style.background = 'rgba(0, 0, 0, 0.8)';
    posterContainer.style.borderRadius = '8px';
    posterContainer.style.padding = '10px';
    posterContainer.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.3)';

    // Ranking number
    const rankingText = document.createElement('div');
    rankingText.style.color = '#fff';
    rankingText.style.fontSize = '14px';
    rankingText.style.fontWeight = 'bold';
    rankingText.style.marginBottom = '8px';
    rankingText.style.textAlign = 'center';
    rankingText.textContent = `${viz3DState.currentMovieIndex + 1} / ${viz3DState.geometricRankings.length}`;
    posterContainer.appendChild(rankingText);

    // Poster image
    console.log('🖼️ Updating poster for:', movie.title, 'poster_path:', movie.poster_path, 'media_type:', movie.media_type);
    const posterUrl = getTMDBImageURL(movie.poster_path, 'w342', movie.media_type, movie.title);
    console.log('🖼️ Poster URL:', posterUrl.substring(0, 100));
    const poster = document.createElement('img');
    poster.src = posterUrl;
    poster.alt = movie.title;
    poster.draggable = true;
    poster.dataset.mediaId = movie.id;
    poster.dataset.mediaTitle = movie.title;
    poster.style.width = '120px';
    poster.style.height = '180px';
    poster.style.objectFit = 'cover';
    poster.style.borderRadius = '4px';
    poster.style.display = 'block';
    poster.style.cursor = 'grab';

    // Add HTML5 drag events to poster
    poster.addEventListener('dragstart', (event) => {
        console.log('🎬 3D SPACE DRAG START - Movie:', movie.title, 'ID:', movie.id);
        event.dataTransfer.setData('mediaId', movie.id);
        event.dataTransfer.setData('mediaTitle', movie.title);
        event.dataTransfer.effectAllowed = 'copy';
        poster.style.opacity = '0.5';
    });

    poster.addEventListener('dragend', (event) => {
        console.log('🎬 3D SPACE DRAG END');
        poster.style.opacity = '1';
    });

    posterContainer.appendChild(poster);

    // Add to container
    viz3DState.container.appendChild(posterContainer);
}


/**
 * Load movies from API
 */
async function loadMovies() {
    try {
        const response = await api.getMedia({ page_size: 500 });
        viz3DState.movies = response.data.items.filter(movie => {
            const cf = movie.custom_fields || {};
            return cf.storytelling && cf.characters && cf.cohesive_vision;
        });

        console.log(`📊 Loaded ${viz3DState.movies.length} movies with 3D criteria`);

        // Calculate rankings
        calculateGeometricRankings();

        // Render movies
        renderMovies();

        // Select top-ranked movie by default
        if (viz3DState.geometricRankings.length > 0) {
            await selectCurrentMovie();
        }
    } catch (error) {
        console.error('❌ Failed to load movies:', error);
    }
}

/**
 * Project 3D point to 2D screen coordinates
 *
 * Coordinate system is oriented so (10,10,10) points upward:
 * - Input: storytelling, characters, vision (0-10 each)
 * - Transform to center at origin with (10,10,10) pointing up
 */
function project3D(storytelling, characters, vision) {
    const centerX = viz3DState.width / 2;
    const centerY = viz3DState.height / 2;
    const scale = 35; // Scale factor for coordinates
    const perspective = 600; // Perspective distance

    // Transform coordinates so (10,10,10) points upward
    // We'll map: storytelling→x, characters→y, vision→z
    // Then rotate the space 45° to make the (10,10,10) corner point up

    // Center the coordinates at 5,5,5 (middle of 0-10 range)
    let x = storytelling - 5;
    let y = characters - 5;
    let z = vision - 5;

    // Apply user rotation
    const rotX = viz3DState.rotation.x * Math.PI / 180;
    const rotY = viz3DState.rotation.y * Math.PI / 180;

    // Rotate around Y axis (horizontal rotation)
    let tempZ = z * Math.cos(rotY) - x * Math.sin(rotY);
    let tempX = z * Math.sin(rotY) + x * Math.cos(rotY);
    let tempY = y;

    // Rotate around X axis (vertical rotation)
    let finalY = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
    let finalZ = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
    let finalX = tempX;

    // Apply perspective projection
    const perspectiveFactor = perspective / (perspective + finalZ * scale);

    return {
        x: centerX + finalX * scale * perspectiveFactor,
        y: centerY - finalY * scale * perspectiveFactor,
        z: finalZ,
        scale: perspectiveFactor
    };
}

/**
 * Render movies in 3D space
 */
function renderMovies() {
    const svg = viz3DState.svg;

    // Clear previous render
    svg.selectAll('.movie-point').remove();
    svg.selectAll('.axis-line').remove();
    svg.selectAll('.axis-label').remove();
    svg.selectAll('.cube-edge').remove();
    svg.selectAll('.cube-face').remove();

    // Draw cube boundary
    drawCube();

    // Draw axes
    drawAxes();

    // Get current selected movie
    const selectedMovie = viz3DState.geometricRankings[viz3DState.currentMovieIndex];

    // Project and sort movies by depth (z-coordinate)
    const projectedMovies = viz3DState.movies.map(movie => {
        const cf = movie.custom_fields;
        const projected = project3D(
            cf.storytelling,
            cf.characters,
            cf.cohesive_vision
        );

        return {
            ...movie,
            projected,
            depth: projected.z,
            isSelected: selectedMovie && movie.id === selectedMovie.id
        };
    });

    // Sort by depth (furthest first for proper occlusion)
    projectedMovies.sort((a, b) => a.depth - b.depth);

    // Render movies
    const points = svg.selectAll('.movie-point')
        .data(projectedMovies);

    points.enter()
        .append('circle')
        .attr('class', 'movie-point')
        .attr('data-media-id', d => d.id)
        .attr('cx', d => d.projected.x)
        .attr('cy', d => d.projected.y)
        .attr('r', d => d.isSelected ? 10 * d.projected.scale : 6 * d.projected.scale)
        .attr('fill', 'url(#depth-gradient)')
        .attr('opacity', d => 0.5 + 0.5 * d.projected.scale)
        .attr('stroke', d => d.isSelected ? '#fbbf24' : '#fff')
        .attr('stroke-width', d => d.isSelected ? 3 : 1)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            if (!d.isSelected) {
                showMovieTooltip(event, d);
                d3.select(this)
                    .attr('r', 10 * d.projected.scale)
                    .attr('stroke-width', 2);
            }
        })
        .on('mouseout', function(event, d) {
            if (!d.isSelected) {
                hideMovieTooltip();
                d3.select(this)
                    .attr('r', 6 * d.projected.scale)
                    .attr('stroke-width', 1);
            }
        })
        .on('click', async function(event, d) {
            // Find this movie in rankings and select it
            const index = viz3DState.geometricRankings.findIndex(m => m.id === d.id);
            if (index !== -1) {
                viz3DState.currentMovieIndex = index;
                await selectCurrentMovie();
            }
        });
}

/**
 * Draw cube boundary showing 0-10 range for all axes
 */
function drawCube() {
    const svg = viz3DState.svg;

    // Define 8 corners of the cube (0-10 range on each axis)
    const corners = [
        [0, 0, 0],   // 0
        [10, 0, 0],  // 1
        [10, 10, 0], // 2
        [0, 10, 0],  // 3
        [0, 0, 10],  // 4
        [10, 0, 10], // 5
        [10, 10, 10],// 6
        [0, 10, 10]  // 7
    ];

    // Project all corners
    const projectedCorners = corners.map(c => project3D(c[0], c[1], c[2]));

    // Define 12 edges of the cube (pairs of corner indices)
    const edges = [
        // Bottom face (z=0)
        [0, 1], [1, 2], [2, 3], [3, 0],
        // Top face (z=10)
        [4, 5], [5, 6], [6, 7], [7, 4],
        // Vertical edges
        [0, 4], [1, 5], [2, 6], [3, 7]
    ];

    // Draw edges
    edges.forEach(([i, j]) => {
        const from = projectedCorners[i];
        const to = projectedCorners[j];

        svg.append('line')
            .attr('class', 'cube-edge')
            .attr('x1', from.x)
            .attr('y1', from.y)
            .attr('x2', to.x)
            .attr('y2', to.y)
            .attr('stroke', '#666')
            .attr('stroke-width', 1.5)
            .attr('opacity', 0.3)
            .attr('stroke-dasharray', '4,4');
    });

    // Label the (10,10,10) corner
    const maxCorner = projectedCorners[6]; // Index 6 is (10,10,10)
    svg.append('text')
        .attr('class', 'axis-label')
        .attr('x', maxCorner.x)
        .attr('y', maxCorner.y - 15)
        .attr('fill', '#fff')
        .attr('font-size', '11px')
        .attr('font-weight', 'bold')
        .attr('text-anchor', 'middle')
        .text('(10,10,10)');
}

/**
 * Draw 3D axes
 */
function drawAxes() {
    const svg = viz3DState.svg;

    const axes = [
        // Storytelling axis (0 to 10) - Red
        { from: [0, 5, 5], to: [10, 5, 5], color: '#ef4444', label: 'Storytelling' },
        // Characters axis (0 to 10) - Green
        { from: [5, 0, 5], to: [5, 10, 5], color: '#10b981', label: 'Characters' },
        // Vision axis (0 to 10) - Blue
        { from: [5, 5, 0], to: [5, 5, 10], color: '#3b82f6', label: 'Vision' }
    ];

    axes.forEach(axis => {
        const from = project3D(...axis.from);
        const to = project3D(...axis.to);

        svg.append('line')
            .attr('class', 'axis-line')
            .attr('x1', from.x)
            .attr('y1', from.y)
            .attr('x2', to.x)
            .attr('y2', to.y)
            .attr('stroke', axis.color)
            .attr('stroke-width', 2.5)
            .attr('opacity', 0.7);

        // Label at end of axis
        svg.append('text')
            .attr('class', 'axis-label')
            .attr('x', to.x)
            .attr('y', to.y - 10)
            .attr('fill', axis.color)
            .attr('font-size', '13px')
            .attr('font-weight', 'bold')
            .attr('text-anchor', 'middle')
            .text(axis.label);
    });
}

/**
 * Show movie tooltip
 */
function showMovieTooltip(event, movie) {
    const cf = movie.custom_fields;

    const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'movie-3d-tooltip')
        .style('position', 'absolute')
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .style('background', 'rgba(0, 0, 0, 0.9)')
        .style('color', '#fff')
        .style('padding', '10px')
        .style('border-radius', '8px')
        .style('font-size', '14px')
        .style('z-index', '1000')
        .style('pointer-events', 'none')
        .html(`
            <div><strong>${movie.title}</strong></div>
            <div style="margin-top: 8px; font-size: 12px;">
                <div><span style="color: #ef4444;">■</span> Storytelling: ${cf.storytelling}</div>
                <div><span style="color: #10b981;">■</span> Characters: ${cf.characters}</div>
                <div><span style="color: #3b82f6;">■</span> Vision: ${cf.cohesive_vision}</div>
            </div>
        `);
}

/**
 * Hide movie tooltip
 */
function hideMovieTooltip() {
    d3.selectAll('.movie-3d-tooltip').remove();
}

/**
 * Refresh visualization
 */
export function refresh3DVisualization() {
    loadMovies();
}
