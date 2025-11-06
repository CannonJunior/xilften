/**
 * Persona Manager
 * Manages critic personas and CAG cache
 */

import * as api from './api-client.js';

// Persona state
const personaState = {
    personas: [],
    currentPersona: null,
    cacheMetrics: null
};

/**
 * Initialize persona manager
 */
export async function initPersonaManager() {
    console.log('🎭 Initializing Persona Manager...');

    // Load personas
    await loadPersonas();

    // Setup event listeners
    setupEventListeners();

    // Load initial cache metrics
    await updateCacheMetrics();

    console.log('✅ Persona Manager initialized');
}

/**
 * Load personas from API
 */
async function loadPersonas() {
    try {
        const response = await api.get('/api/personas/list');

        if (response.success) {
            personaState.personas = response.data;
            populatePersonaSelector();
            console.log(`📚 Loaded ${personaState.personas.length} personas`);
        }
    } catch (error) {
        console.error('❌ Failed to load personas:', error);
    }
}

/**
 * Populate persona selector dropdown
 */
function populatePersonaSelector() {
    const select = document.getElementById('persona-select');
    if (!select) return;

    // Clear existing options except default
    while (select.options.length > 1) {
        select.remove(1);
    }

    // Add persona options
    personaState.personas.forEach(persona => {
        const option = document.createElement('option');
        option.value = persona.id;
        option.textContent = `${persona.name} - ${persona.title}`;
        select.appendChild(option);
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const personaSelect = document.getElementById('persona-select');
    const clearCacheBtn = document.getElementById('clear-cache-btn');

    if (personaSelect) {
        personaSelect.addEventListener('change', handlePersonaChange);
    }

    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', handleClearCache);
    }
}

/**
 * Handle persona selection change
 */
async function handlePersonaChange(event) {
    const personaId = event.target.value;

    if (!personaId) {
        // No persona selected - clear cache
        await handleClearCache();
        return;
    }

    try {
        console.log(`🎭 Loading persona: ${personaId}`);

        const response = await api.post('/api/personas/load', {
            persona_id: personaId
        });

        if (response.success) {
            personaState.currentPersona = personaId;
            await updateCacheMetrics();

            // Show success message
            showPersonaNotification(personaId, 'loaded');
        }
    } catch (error) {
        console.error('❌ Failed to load persona:', error);
        showPersonaNotification(personaId, 'error');

        // Reset selector
        event.target.value = '';
    }
}

/**
 * Handle clear cache button
 */
async function handleClearCache() {
    try {
        console.log('🧹 Clearing CAG cache...');

        const response = await api.post('/api/personas/cache/clear');

        if (response.success) {
            personaState.currentPersona = null;
            await updateCacheMetrics();

            // Reset persona selector
            const select = document.getElementById('persona-select');
            if (select) {
                select.value = '';
            }

            showPersonaNotification(null, 'cleared');
        }
    } catch (error) {
        console.error('❌ Failed to clear cache:', error);
    }
}

/**
 * Update cache metrics display
 */
async function updateCacheMetrics() {
    try {
        const response = await api.get('/api/personas/cache/metrics');

        if (response.success) {
            personaState.cacheMetrics = response.data;
            renderCacheMetrics();
        }
    } catch (error) {
        console.error('❌ Failed to get cache metrics:', error);
    }
}

/**
 * Render cache metrics UI
 */
function renderCacheMetrics() {
    const metrics = personaState.cacheMetrics;
    if (!metrics) return;

    const usageSpan = document.getElementById('cache-usage');
    const barFill = document.getElementById('cache-bar-fill');

    if (usageSpan) {
        usageSpan.textContent = `${metrics.size_used_mb} MB / ${metrics.size_limit_mb} MB`;
    }

    if (barFill) {
        barFill.style.width = `${metrics.usage_percent}%`;

        // Color code based on usage
        if (metrics.usage_percent > 80) {
            barFill.style.backgroundColor = '#ef4444'; // Red
        } else if (metrics.usage_percent > 50) {
            barFill.style.backgroundColor = '#f59e0b'; // Orange
        } else {
            barFill.style.backgroundColor = '#10b981'; // Green
        }
    }
}

/**
 * Show persona notification
 */
function showPersonaNotification(personaId, action) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    let message = '';
    let icon = '';

    if (action === 'loaded') {
        const persona = personaState.personas.find(p => p.id === personaId);
        message = `🎭 Now speaking as <strong>${persona.name}</strong>. AI responses will adopt their critical style and perspective.`;
        icon = '🎭';
    } else if (action === 'cleared') {
        message = '🧹 Persona cache cleared. AI responses will use the default style.';
        icon = '🧹';
    } else if (action === 'error') {
        message = '❌ Failed to load persona. Please try again.';
        icon = '❌';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant persona-notification';
    messageDiv.innerHTML = `<p>${message}</p>`;

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.classList.add('fade-out');
        setTimeout(() => messageDiv.remove(), 500);
    }, 5000);
}

/**
 * Get current persona ID
 */
export function getCurrentPersona() {
    return personaState.currentPersona;
}

/**
 * Get persona profile by ID
 */
export async function getPersonaProfile(personaId) {
    try {
        const response = await api.get(`/api/personas/${personaId}`);
        return response.success ? response.data : null;
    } catch (error) {
        console.error(`❌ Failed to get persona ${personaId}:`, error);
        return null;
    }
}
