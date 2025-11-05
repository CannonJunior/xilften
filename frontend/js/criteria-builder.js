/**
 * Criteria Builder UI Module.
 *
 * Interactive interface for creating custom recommendation criteria.
 */

import * as API from './api-client.js';

// State
let availableFields = [];
let currentCriteria = {};
let modalElement = null;

/**
 * Initialize criteria builder module.
 */
export async function init() {
    console.log('Initializing criteria builder...');

    // Load available fields
    await loadAvailableFields();

    // Listen for open events
    document.addEventListener('open-criteria-builder', openBuilder);

    console.log('Criteria builder initialized');
}

/**
 * Load available criteria fields from API.
 */
async function loadAvailableFields() {
    try {
        const response = await API.getAvailableFields();
        availableFields = response.fields;
        console.log(`Loaded ${availableFields.length} available fields`);
    } catch (error) {
        console.error('Failed to load available fields:', error);
    }
}

/**
 * Open the criteria builder modal.
 */
function openBuilder() {
    if (modalElement) {
        modalElement.remove();
    }

    modalElement = createBuilderModal();
    document.body.appendChild(modalElement);

    // Reset state
    currentCriteria = {};
}

/**
 * Create the criteria builder modal.
 *
 * @returns {HTMLElement} - Modal element
 */
function createBuilderModal() {
    const modal = document.createElement('div');
    modal.className = 'criteria-builder-modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h2>Build Custom Criteria</h2>
                <button class="modal-close" aria-label="Close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="builder-instructions">
                    <p>Select fields and configure criteria to create a custom recommendation preset.</p>
                </div>

                <div class="builder-content">
                    <!-- Field selector -->
                    <div class="field-selector">
                        <h3>Available Fields</h3>
                        <div id="field-list" class="field-list"></div>
                    </div>

                    <!-- Criteria configurator -->
                    <div class="criteria-config">
                        <h3>Active Criteria</h3>
                        <div id="criteria-list" class="criteria-list">
                            <p class="empty-criteria">No criteria selected yet. Select fields from the left.</p>
                        </div>
                    </div>
                </div>

                <div class="builder-preview">
                    <h3>Preview</h3>
                    <button id="preview-button" class="secondary-button">Test Criteria</button>
                    <div id="preview-results"></div>
                </div>
            </div>
            <div class="modal-footer">
                <div class="preset-save">
                    <input type="text" id="preset-name" placeholder="Preset Name" class="preset-name-input">
                    <textarea id="preset-description" placeholder="Description (optional)" class="preset-description-input" rows="2"></textarea>
                </div>
                <div class="modal-actions">
                    <button id="save-preset-button" class="primary-button">Save as Preset</button>
                    <button id="use-once-button" class="secondary-button">Use Once</button>
                    <button id="cancel-button" class="secondary-button">Cancel</button>
                </div>
            </div>
        </div>
    `;

    // Setup event listeners
    setupModalListeners(modal);

    // Populate field list
    populateFieldList(modal);

    return modal;
}

/**
 * Setup event listeners for the modal.
 *
 * @param {HTMLElement} modal - Modal element
 */
function setupModalListeners(modal) {
    // Close button
    const closeButton = modal.querySelector('.modal-close');
    const overlay = modal.querySelector('.modal-overlay');
    const cancelButton = modal.querySelector('#cancel-button');

    [closeButton, overlay, cancelButton].forEach(el => {
        el?.addEventListener('click', closeBuilder);
    });

    // Preview button
    const previewButton = modal.querySelector('#preview-button');
    previewButton?.addEventListener('click', previewCriteria);

    // Save preset button
    const saveButton = modal.querySelector('#save-preset-button');
    saveButton?.addEventListener('click', savePreset);

    // Use once button
    const useOnceButton = modal.querySelector('#use-once-button');
    useOnceButton?.addEventListener('click', useOnce);
}

/**
 * Populate the field list with available fields.
 *
 * @param {HTMLElement} modal - Modal element
 */
function populateFieldList(modal) {
    const fieldList = modal.querySelector('#field-list');
    if (!fieldList) return;

    availableFields.forEach(field => {
        const fieldItem = document.createElement('div');
        fieldItem.className = 'field-item';
        fieldItem.innerHTML = `
            <div class="field-info">
                <strong>${field.display_name}</strong>
                <span class="field-type">${field.field_type}</span>
                <p class="field-description">${field.description}</p>
            </div>
            <button class="add-field-button" data-field="${field.field_name}">Add</button>
        `;

        const addButton = fieldItem.querySelector('.add-field-button');
        addButton.addEventListener('click', () => addCriterion(field));

        fieldList.appendChild(fieldItem);
    });
}

/**
 * Add a criterion to the active criteria.
 *
 * @param {Object} field - Field object
 */
function addCriterion(field) {
    // Initialize criterion
    currentCriteria[field.field_name] = {
        weight: 0.5
    };

    // Render criteria list
    renderCriteriaList();
}

/**
 * Render the active criteria list.
 */
function renderCriteriaList() {
    const criteriaList = modalElement.querySelector('#criteria-list');
    if (!criteriaList) return;

    if (Object.keys(currentCriteria).length === 0) {
        criteriaList.innerHTML = '<p class="empty-criteria">No criteria selected yet. Select fields from the left.</p>';
        return;
    }

    criteriaList.innerHTML = '';

    Object.entries(currentCriteria).forEach(([fieldName, config]) => {
        const field = availableFields.find(f => f.field_name === fieldName);
        if (!field) return;

        const criterionItem = createCriterionEditor(field, config);
        criteriaList.appendChild(criterionItem);
    });
}

/**
 * Create a criterion editor.
 *
 * @param {Object} field - Field object
 * @param {Object} config - Criterion configuration
 * @returns {HTMLElement} - Criterion editor element
 */
function createCriterionEditor(field, config) {
    const item = document.createElement('div');
    item.className = 'criterion-item';

    let configHTML = '';

    // Weight slider
    configHTML += `
        <div class="criterion-header">
            <strong>${field.display_name}</strong>
            <button class="remove-criterion" data-field="${field.field_name}">&times;</button>
        </div>
        <div class="criterion-weight">
            <label>Weight: <span class="weight-value">${config.weight}</span></label>
            <input type="range" class="weight-slider" min="0" max="1" step="0.1" value="${config.weight}" data-field="${field.field_name}">
        </div>
    `;

    // Field-specific configuration
    if (field.supports_min_max) {
        configHTML += `
            <div class="criterion-range">
                <label>Min:
                    <input type="number" class="min-input" placeholder="Min" value="${config.min || ''}" data-field="${field.field_name}">
                </label>
                <label>Max:
                    <input type="number" class="max-input" placeholder="Max" value="${config.max || ''}" data-field="${field.field_name}">
                </label>
            </div>
        `;
    }

    if (field.supports_values) {
        const currentValues = config.values || [];
        configHTML += `
            <div class="criterion-values">
                <label>Values (comma-separated):</label>
                <input type="text" class="values-input" placeholder="e.g., sci-fi, action, drama" value="${currentValues.join(', ')}" data-field="${field.field_name}">
                ${field.example_values ? `<small>Examples: ${field.example_values.join(', ')}</small>` : ''}
            </div>
        `;
    }

    item.innerHTML = configHTML;

    // Setup event listeners
    const removeButton = item.querySelector('.remove-criterion');
    removeButton.addEventListener('click', () => removeCriterion(field.field_name));

    const weightSlider = item.querySelector('.weight-slider');
    const weightValue = item.querySelector('.weight-value');
    weightSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        weightValue.textContent = value;
        currentCriteria[field.field_name].weight = value;
    });

    if (field.supports_min_max) {
        const minInput = item.querySelector('.min-input');
        const maxInput = item.querySelector('.max-input');

        minInput.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                currentCriteria[field.field_name].min = value;
            } else {
                delete currentCriteria[field.field_name].min;
            }
        });

        maxInput.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                currentCriteria[field.field_name].max = value;
            } else {
                delete currentCriteria[field.field_name].max;
            }
        });
    }

    if (field.supports_values) {
        const valuesInput = item.querySelector('.values-input');
        valuesInput.addEventListener('change', (e) => {
            const values = e.target.value
                .split(',')
                .map(v => v.trim())
                .filter(v => v.length > 0);

            if (values.length > 0) {
                currentCriteria[field.field_name].values = values;
            } else {
                delete currentCriteria[field.field_name].values;
            }
        });
    }

    return item;
}

/**
 * Remove a criterion from the active criteria.
 *
 * @param {string} fieldName - Field name
 */
function removeCriterion(fieldName) {
    delete currentCriteria[fieldName];
    renderCriteriaList();
}

/**
 * Preview criteria with test recommendations.
 */
async function previewCriteria() {
    const previewResults = modalElement.querySelector('#preview-results');
    if (!previewResults) return;

    if (Object.keys(currentCriteria).length === 0) {
        previewResults.innerHTML = '<p class="error-message">Please add at least one criterion.</p>';
        return;
    }

    previewResults.innerHTML = '<p class="loading-message">Generating preview...</p>';

    try {
        const response = await API.getRecommendations({
            criteria_config: currentCriteria,
            limit: 5
        });

        previewResults.innerHTML = `
            <div class="preview-stats">
                Found <strong>${response.recommendations.length}</strong> recommendations
                from <strong>${response.total_candidates}</strong> candidates
            </div>
            <div class="preview-list">
                ${response.recommendations.map((item, i) => `
                    <div class="preview-item">
                        <span class="preview-rank">#${i + 1}</span>
                        <span class="preview-title">${item.media.title}</span>
                        <span class="preview-score">${(item.score * 100).toFixed(0)}%</span>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Preview failed:', error);
        previewResults.innerHTML = '<p class="error-message">Failed to generate preview.</p>';
    }
}

/**
 * Save criteria as a preset.
 */
async function savePreset() {
    const nameInput = modalElement.querySelector('#preset-name');
    const descInput = modalElement.querySelector('#preset-description');

    const name = nameInput?.value.trim();
    const description = descInput?.value.trim();

    if (!name) {
        alert('Please enter a preset name.');
        nameInput?.focus();
        return;
    }

    if (Object.keys(currentCriteria).length === 0) {
        alert('Please add at least one criterion.');
        return;
    }

    try {
        await API.createCriteriaPreset({
            name,
            description: description || null,
            criteria_config: currentCriteria,
            is_default: false
        });

        alert(`Preset "${name}" saved successfully!`);
        closeBuilder();

        // Trigger preset reload in recommendations view
        const event = new CustomEvent('presets-updated');
        document.dispatchEvent(event);
    } catch (error) {
        console.error('Failed to save preset:', error);
        alert('Failed to save preset. Please try again.');
    }
}

/**
 * Use criteria once without saving.
 */
async function useOnce() {
    if (Object.keys(currentCriteria).length === 0) {
        alert('Please add at least one criterion.');
        return;
    }

    try {
        // Trigger recommendation generation with custom criteria
        const event = new CustomEvent('use-custom-criteria', {
            detail: { criteria: currentCriteria }
        });
        document.dispatchEvent(event);

        closeBuilder();
    } catch (error) {
        console.error('Failed to use criteria:', error);
    }
}

/**
 * Close the criteria builder modal.
 */
function closeBuilder() {
    if (modalElement) {
        modalElement.remove();
        modalElement = null;
    }
}
