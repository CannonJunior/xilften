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

// Visualization state
const viz3DState = {
    container: null,
    svg: null,
    width: 600,
    height: 600,
    movies: [],
    rotation: { x: 30, y: 45 }, // Rotation angles in degrees
    isDragging: false,
    lastMouse: { x: 0, y: 0 }
};

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

        renderMovies();
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
            depth: projected.z
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
        .attr('r', d => 6 * d.projected.scale)
        .attr('fill', 'url(#depth-gradient)')
        .attr('opacity', d => 0.5 + 0.5 * d.projected.scale)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            showMovieTooltip(event, d);
            d3.select(this)
                .attr('r', 10 * d.projected.scale)
                .attr('stroke-width', 2);
        })
        .on('mouseout', function(event, d) {
            hideMovieTooltip();
            d3.select(this)
                .attr('r', 6 * d.projected.scale)
                .attr('stroke-width', 1);
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
