/**
 * Calendar Module
 * D3.js-powered calendar with event visualization
 */

import * as api from './api-client.js';

// Calendar state
let calendarState = {
    currentDate: new Date(),
    events: [],
    selectedDate: null,
    container: null,
};

/**
 * Initialize calendar
 */
export function initCalendar() {
    console.log('📅 Initializing D3.js calendar...');

    // Setup month navigation
    setupMonthNavigation();

    // Load and render calendar when view becomes active
    window.addEventListener('viewChanged', (event) => {
        if (event.detail.view === 'calendar') {
            loadCalendarData();
        }
    });
}

/**
 * Setup month navigation
 */
function setupMonthNavigation() {
    const prevButton = document.getElementById('prev-month');
    const nextButton = document.getElementById('next-month');

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            changeMonth(-1);
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', () => {
            changeMonth(1);
        });
    }
}

/**
 * Change month
 *
 * @param {number} direction - -1 for previous, 1 for next
 */
function changeMonth(direction) {
    const newDate = new Date(calendarState.currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    calendarState.currentDate = newDate;

    updateMonthDisplay();
    loadCalendarData();
}

/**
 * Update month display text
 */
function updateMonthDisplay() {
    const monthDisplay = document.getElementById('current-month');
    if (monthDisplay) {
        const monthName = calendarState.currentDate.toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });
        monthDisplay.textContent = monthName;
    }
}

/**
 * Load calendar data for current month
 */
async function loadCalendarData() {
    try {
        const year = calendarState.currentDate.getFullYear();
        const month = calendarState.currentDate.getMonth();

        // Get first and last day of month
        const startDate = new Date(year, month, 1);
        const endDate = new Date(year, month + 1, 0);

        const params = {
            start_date: startDate.toISOString().split('T')[0],
            end_date: endDate.toISOString().split('T')[0]
        };

        // Try to fetch events from API
        try {
            const response = await api.getCalendarEvents(params);
            calendarState.events = response.data || [];
        } catch (error) {
            console.warn('⚠️ API not available, using sample events');
            calendarState.events = generateSampleEvents(year, month);
        }

        renderCalendar();
        updateMonthDisplay();

    } catch (error) {
        console.error('❌ Failed to load calendar data:', error);
        calendarState.events = [];
        renderCalendar();
    }
}

/**
 * Generate sample events for development
 *
 * @param {number} year - Year
 * @param {number} month - Month (0-indexed)
 * @returns {Array} - Sample events
 */
function generateSampleEvents(year, month) {
    return [
        {
            id: '1',
            event_date: new Date(year, month, 5).toISOString().split('T')[0],
            event_type: 'watch',
            title: 'The Matrix',
            color: '#FF6B6B'
        },
        {
            id: '2',
            event_date: new Date(year, month, 15).toISOString().split('T')[0],
            event_type: 'release',
            title: 'New Sci-Fi Release',
            color: '#4ECDC4'
        },
        {
            id: '3',
            event_date: new Date(year, month, 20).toISOString().split('T')[0],
            event_type: 'review',
            title: 'Write Blade Runner review',
            color: '#95E1D3'
        },
    ];
}

/**
 * Render calendar with D3.js
 */
function renderCalendar() {
    const container = d3.select('#calendar-container');
    container.html(''); // Clear previous content

    carouselState.container = container;

    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();

    // Get calendar data
    const calendarData = generateCalendarData(year, month);

    // Render day names
    renderDayNames(container);

    // Render calendar grid
    renderCalendarGrid(container, calendarData);

    console.log(`✅ Calendar rendered for ${year}-${month + 1}`);
}

/**
 * Generate calendar data structure
 *
 * @param {number} year - Year
 * @param {number} month - Month (0-indexed)
 * @returns {Array} - Calendar data with weeks and days
 */
function generateCalendarData(year, month) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startingDayOfWeek = firstDay.getDay();
    const totalDays = lastDay.getDate();

    const weeks = [];
    let currentWeek = [];

    // Fill in days from previous month
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
        currentWeek.push({
            day: prevMonthLastDay - i,
            date: new Date(year, month - 1, prevMonthLastDay - i),
            isCurrentMonth: false,
            events: []
        });
    }

    // Fill in current month days
    for (let day = 1; day <= totalDays; day++) {
        const date = new Date(year, month, day);
        const dateString = date.toISOString().split('T')[0];
        const dayEvents = calendarState.events.filter(e => e.event_date === dateString);

        currentWeek.push({
            day: day,
            date: date,
            isCurrentMonth: true,
            isToday: isToday(date),
            events: dayEvents
        });

        if (currentWeek.length === 7) {
            weeks.push(currentWeek);
            currentWeek = [];
        }
    }

    // Fill in days from next month
    if (currentWeek.length > 0) {
        let nextMonthDay = 1;
        while (currentWeek.length < 7) {
            currentWeek.push({
                day: nextMonthDay,
                date: new Date(year, month + 1, nextMonthDay),
                isCurrentMonth: false,
                events: []
            });
            nextMonthDay++;
        }
        weeks.push(currentWeek);
    }

    return weeks;
}

/**
 * Check if date is today
 *
 * @param {Date} date - Date to check
 * @returns {boolean} - True if date is today
 */
function isToday(date) {
    const today = new Date();
    return date.toDateString() === today.toDateString();
}

/**
 * Render day names header
 *
 * @param {Object} container - D3 selection
 */
function renderDayNames(container) {
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    const dayNamesContainer = container
        .append('div')
        .attr('class', 'calendar-day-names');

    dayNamesContainer
        .selectAll('.day-name')
        .data(dayNames)
        .enter()
        .append('div')
        .attr('class', 'day-name')
        .text(d => d);
}

/**
 * Render calendar grid
 *
 * @param {Object} container - D3 selection
 * @param {Array} weeks - Calendar weeks data
 */
function renderCalendarGrid(container, weeks) {
    const gridContainer = container
        .append('div')
        .attr('class', 'calendar-grid');

    // Flatten weeks into days
    const allDays = weeks.flat();

    // Create day cells
    const dayCells = gridContainer
        .selectAll('.calendar-day')
        .data(allDays)
        .enter()
        .append('div')
        .attr('class', d => {
            let classes = 'calendar-day';
            if (!d.isCurrentMonth) classes += ' other-month';
            if (d.isToday) classes += ' today';
            if (d.events.length > 0) classes += ' has-events';
            return classes;
        })
        .on('click', (event, d) => handleDayClick(d));

    // Add day number
    dayCells
        .append('div')
        .attr('class', 'day-number')
        .text(d => d.day);

    // Add event indicators
    dayCells.each(function(d) {
        const cell = d3.select(this);

        if (d.events.length > 0) {
            const eventsContainer = cell
                .append('div')
                .attr('class', 'day-events');

            // Add event indicator bars (max 3 visible)
            d.events.slice(0, 3).forEach(event => {
                eventsContainer
                    .append('div')
                    .attr('class', `event-indicator ${event.event_type}`)
                    .style('background-color', event.color);
            });

            // Add icon if there are events
            if (d.events.length > 0) {
                const iconsContainer = cell
                    .append('div')
                    .attr('class', 'day-icons');

                iconsContainer
                    .append('div')
                    .attr('class', 'event-icon')
                    .text('📅');
            }
        }
    });

    // Add entrance animation
    dayCells
        .style('opacity', 0)
        .transition()
        .duration(300)
        .delay((d, i) => i * 10)
        .style('opacity', 1);
}

/**
 * Handle day cell click
 *
 * @param {Object} dayData - Day data
 */
function handleDayClick(dayData) {
    if (!dayData.isCurrentMonth) {
        return;
    }

    carouselState.selectedDate = dayData.date;

    // Remove previous selection
    d3.selectAll('.calendar-day').classed('selected', false);

    // Add selection to clicked day
    d3.selectAll('.calendar-day')
        .filter(d => d === dayData)
        .classed('selected', true);

    // Show event detail modal if there are events
    if (dayData.events.length > 0) {
        showEventDetailModal(dayData);
    } else {
        // Show add event option
        console.log('📅 No events for this day, show add event option');
        // TODO: Implement add event modal
    }
}

/**
 * Show event detail modal
 *
 * @param {Object} dayData - Day data with events
 */
function showEventDetailModal(dayData) {
    // Remove existing modal if any
    d3.select('.event-detail-overlay').remove();

    const overlay = d3.select('body')
        .append('div')
        .attr('class', 'event-detail-overlay')
        .on('click', function(event) {
            if (event.target === this) {
                closeEventDetailModal();
            }
        });

    const modal = overlay
        .append('div')
        .attr('class', 'event-detail-modal');

    // Header
    const header = modal
        .append('div')
        .attr('class', 'event-detail-header');

    header
        .append('h3')
        .attr('class', 'event-detail-title')
        .text(dayData.date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }));

    header
        .append('button')
        .attr('class', 'close-button')
        .html('×')
        .on('click', closeEventDetailModal);

    // Content
    const content = modal
        .append('div')
        .attr('class', 'event-detail-content');

    const eventList = content
        .append('div')
        .attr('class', 'event-list');

    // Render events
    const eventItems = eventList
        .selectAll('.event-item')
        .data(dayData.events)
        .enter()
        .append('div')
        .attr('class', d => `event-item ${d.event_type}`);

    eventItems.each(function(event) {
        const item = d3.select(this);

        const info = item
            .append('div')
            .attr('class', 'event-item-info');

        info
            .append('h4')
            .text(event.title);

        info
            .append('p')
            .text(`Type: ${event.event_type}`);

        if (event.description) {
            info
                .append('p')
                .text(event.description);
        }
    });
}

/**
 * Close event detail modal
 */
function closeEventDetailModal() {
    d3.select('.event-detail-overlay')
        .transition()
        .duration(200)
        .style('opacity', 0)
        .remove();
}

/**
 * Render calendar heatmap view (alternative visualization)
 */
export function renderHeatmapView() {
    const container = d3.select('#calendar-container');
    container.html('');

    // Create heatmap for year view
    const year = calendarState.currentDate.getFullYear();
    const weeks = 52;

    const heatmapContainer = container
        .append('div')
        .attr('class', 'calendar-heatmap');

    // Generate year data
    const yearData = [];
    for (let week = 0; week < weeks; week++) {
        for (let day = 0; day < 7; day++) {
            const date = new Date(year, 0, 1 + week * 7 + day);
            if (date.getFullYear() === year) {
                const dateString = date.toISOString().split('T')[0];
                const dayEvents = calendarState.events.filter(e => e.event_date === dateString);

                yearData.push({
                    date: date,
                    week: week,
                    day: day,
                    intensity: Math.min(dayEvents.length, 5),
                    events: dayEvents
                });
            }
        }
    }

    // Render heatmap cells
    const cells = heatmapContainer
        .selectAll('.heatmap-cell')
        .data(yearData)
        .enter()
        .append('div')
        .attr('class', d => `heatmap-cell intensity-${d.intensity}`)
        .attr('title', d => {
            const dateStr = d.date.toLocaleDateString();
            return d.events.length > 0
                ? `${dateStr}: ${d.events.length} event(s)`
                : dateStr;
        })
        .on('click', (event, d) => handleDayClick(d));

    console.log('🔥 Heatmap view rendered');
}

// Initialize calendar when module loads
initCalendar();

// Export functions
export { loadCalendarData, renderCalendar, changeMonth };
