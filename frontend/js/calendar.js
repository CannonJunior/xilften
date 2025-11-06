/**
 * Calendar Module - Month Grid + Day Detail Card
 * D3.js-powered calendar with month view and page-turning day card
 */

import * as api from './api-client.js';

// Calendar state
let calendarState = {
    currentDate: new Date(),
    selectedDate: new Date(),
    events: [],
    container: null,
    isInitialized: false,
    isAnimating: false,
};

/**
 * Initialize calendar
 */
export function initCalendar() {
    console.log('📅 Initializing calendar sidebar...');

    if (calendarState.isInitialized) {
        return;
    }

    const monthGrid = document.getElementById('calendar-month-grid');
    const dayCard = document.getElementById('day-detail-card');

    if (!monthGrid || !dayCard) {
        console.error('❌ Calendar containers not found');
        return;
    }

    calendarState.isInitialized = true;

    // Setup mousewheel scrolling
    setupMousewheelScrolling();

    // Load and render initial calendar
    loadCalendarData();

    console.log('✅ Calendar sidebar initialized');
}

/**
 * Setup mousewheel scrolling for day navigation
 */
function setupMousewheelScrolling() {
    const sidebar = document.getElementById('calendar-sidebar');
    if (!sidebar) return;

    let scrollTimeout;

    sidebar.addEventListener('wheel', (event) => {
        event.preventDefault();

        // Don't scroll if animation is in progress
        if (calendarState.isAnimating) {
            return;
        }

        // Determine scroll direction
        const delta = Math.sign(event.deltaY);

        // Change selected date by delta days
        const newDate = new Date(calendarState.selectedDate);
        newDate.setDate(newDate.getDate() + delta);

        // Check if we crossed a month boundary
        const crossedMonth = newDate.getMonth() !== calendarState.selectedDate.getMonth();

        calendarState.selectedDate = newDate;

        if (crossedMonth) {
            calendarState.currentDate = new Date(newDate);
        }

        // Trigger page turn animation
        const direction = delta > 0 ? 'forward' : 'backward';
        triggerPageTurn(direction);

        // Debounce the rendering - 16ms for 3x faster (~60fps)
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            if (crossedMonth) {
                renderMonthGrid();
            } else {
                updateMonthGridSelection();
            }
            renderDayCard();
        }, 16);
    }, { passive: false });
}

/**
 * Trigger page turn animation
 *
 * @param {string} direction - 'forward' or 'backward'
 */
function triggerPageTurn(direction) {
    const dayCard = document.getElementById('day-detail-card');
    if (!dayCard) return;

    calendarState.isAnimating = true;

    // Remove any existing animation classes
    dayCard.classList.remove('page-turn-forward', 'page-turn-backward');

    // Force reflow to restart animation
    void dayCard.offsetWidth;

    // Add appropriate animation class
    const className = direction === 'forward' ? 'page-turn-forward' : 'page-turn-backward';
    dayCard.classList.add(className);

    // Remove animation class after animation completes
    setTimeout(() => {
        dayCard.classList.remove(className);
        calendarState.isAnimating = false;
    }, 600); // Match animation duration
}

/**
 * Load calendar data
 */
async function loadCalendarData() {
    try {
        // Calculate date range for events
        const year = calendarState.currentDate.getFullYear();
        const month = calendarState.currentDate.getMonth();

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
            calendarState.events = generateSampleEvents();
        }

        renderMonthGrid();
        renderDayCard();

    } catch (error) {
        console.error('❌ Failed to load calendar data:', error);
        calendarState.events = [];
        renderMonthGrid();
        renderDayCard();
    }
}

/**
 * Generate sample events for development
 *
 * @returns {Array} - Sample events
 */
function generateSampleEvents() {
    const events = [];
    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();

    // Generate some random events for current month
    for (let day = 1; day <= 28; day++) {
        if (Math.random() > 0.7) { // 30% chance of event
            const eventDate = new Date(year, month, day);

            const eventTypes = ['watch', 'release', 'review'];
            const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];

            const titles = {
                watch: ['The Matrix', 'Blade Runner', 'Inception', 'Interstellar'],
                release: ['New Sci-Fi Release', 'Upcoming Documentary', 'New Series Premiere'],
                review: ['Write review', 'Update ratings', 'Add comments']
            };

            events.push({
                id: `event-${day}`,
                event_date: eventDate.toISOString().split('T')[0],
                event_type: eventType,
                title: titles[eventType][Math.floor(Math.random() * titles[eventType].length)],
            });
        }
    }

    return events;
}

/**
 * Render month calendar grid
 */
function renderMonthGrid() {
    const container = d3.select('#calendar-month-grid');
    container.html(''); // Clear previous content

    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();

    // Update month/year header
    const monthYearElement = document.getElementById('calendar-month-year');
    if (monthYearElement) {
        monthYearElement.textContent = calendarState.currentDate.toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });
    }

    // Add weekday headers
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    weekdays.forEach(day => {
        container
            .append('div')
            .attr('class', 'calendar-weekday-header')
            .text(day);
    });

    // Generate calendar data
    const calendarData = generateMonthCalendarData(year, month);

    // Render day cells
    calendarData.forEach(dayData => {
        const cell = container
            .append('div')
            .attr('class', () => {
                let classes = 'calendar-day-cell';
                if (!dayData.isCurrentMonth) classes += ' other-month';
                if (dayData.isToday) classes += ' today';
                if (dayData.isSelected) classes += ' selected';
                if (dayData.hasEvents) classes += ' has-events';
                return classes;
            })
            .text(dayData.day)
            .on('click', () => handleDayClick(dayData));
    });

    console.log(`✅ Month grid rendered for ${year}-${month + 1}`);
}

/**
 * Update month grid selection without full re-render
 */
function updateMonthGridSelection() {
    const cells = d3.selectAll('.calendar-day-cell');

    cells.each(function() {
        const cell = d3.select(this);
        const dayNumber = parseInt(cell.text());
        const isOtherMonth = cell.classed('other-month');

        // Only select cells from the current month that match the selected day
        const isSelected = !isOtherMonth &&
                          dayNumber === calendarState.selectedDate.getDate() &&
                          calendarState.selectedDate.getMonth() === calendarState.currentDate.getMonth();

        cell.classed('selected', isSelected);
    });
}

/**
 * Generate month calendar data
 *
 * @param {number} year - Year
 * @param {number} month - Month (0-indexed)
 * @returns {Array} - Calendar data
 */
function generateMonthCalendarData(year, month) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startingDayOfWeek = firstDay.getDay();
    const totalDays = lastDay.getDate();

    const days = [];

    // Fill in days from previous month
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
        const day = prevMonthLastDay - i;
        const date = new Date(year, month - 1, day);
        days.push({
            day: day,
            date: date,
            isCurrentMonth: false,
            isToday: false,
            isSelected: false,
            hasEvents: false
        });
    }

    // Fill in current month days
    for (let day = 1; day <= totalDays; day++) {
        const date = new Date(year, month, day);
        const dateString = date.toISOString().split('T')[0];
        const dayEvents = calendarState.events.filter(e => e.event_date === dateString);

        days.push({
            day: day,
            date: date,
            isCurrentMonth: true,
            isToday: isToday(date),
            isSelected: isSameDay(date, calendarState.selectedDate),
            hasEvents: dayEvents.length > 0
        });
    }

    // Fill in days from next month
    const remainingCells = 42 - days.length; // 6 rows * 7 days
    for (let day = 1; day <= remainingCells; day++) {
        const date = new Date(year, month + 1, day);
        days.push({
            day: day,
            date: date,
            isCurrentMonth: false,
            isToday: false,
            isSelected: false,
            hasEvents: false
        });
    }

    return days;
}

/**
 * Render day detail card
 */
function renderDayCard() {
    const container = d3.select('#day-detail-card');
    container.html(''); // Clear previous content

    const selectedDate = calendarState.selectedDate;
    const dateString = selectedDate.toISOString().split('T')[0];
    const dayEvents = calendarState.events.filter(e => e.event_date === dateString);

    // Header
    const header = container
        .append('div')
        .attr('class', 'day-detail-header');

    const dateDiv = header
        .append('div')
        .attr('class', 'day-detail-date');

    dateDiv
        .append('div')
        .attr('class', 'day-detail-number')
        .text(selectedDate.getDate());

    dateDiv
        .append('div')
        .attr('class', 'day-detail-weekday')
        .text(selectedDate.toLocaleDateString('en-US', { weekday: 'long' }));

    header
        .append('div')
        .attr('class', 'day-detail-full-date')
        .text(selectedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }));

    // Events section
    const eventsSection = container
        .append('div')
        .attr('class', 'day-detail-events');

    if (dayEvents.length > 0) {
        eventsSection
            .append('div')
            .attr('class', 'day-detail-events-title')
            .text(`Events (${dayEvents.length})`);

        dayEvents.forEach(event => {
            const eventDiv = eventsSection
                .append('div')
                .attr('class', `day-detail-event ${event.event_type}`);

            const icon = getEventIcon(event.event_type);
            eventDiv
                .append('div')
                .attr('class', 'day-detail-event-icon')
                .text(icon);

            const content = eventDiv
                .append('div')
                .attr('class', 'day-detail-event-content');

            content
                .append('div')
                .attr('class', 'day-detail-event-title')
                .text(event.title);

            content
                .append('div')
                .attr('class', 'day-detail-event-type')
                .text(event.event_type);
        });
    } else {
        eventsSection
            .append('div')
            .attr('class', 'day-detail-empty')
            .text('No events scheduled for this day');
    }
}

/**
 * Get event icon by type
 *
 * @param {string} eventType - Event type
 * @returns {string} - Emoji icon
 */
function getEventIcon(eventType) {
    const icons = {
        watch: '🎬',
        release: '🎉',
        review: '✍️',
        custom: '📅'
    };
    return icons[eventType] || icons.custom;
}

/**
 * Handle day cell click
 *
 * @param {Object} dayData - Day data
 */
function handleDayClick(dayData) {
    if (!dayData.isCurrentMonth) {
        // Change month if clicking on adjacent month days
        const newMonth = new Date(calendarState.currentDate);
        if (dayData.day > 15) {
            newMonth.setMonth(newMonth.getMonth() - 1);
        } else {
            newMonth.setMonth(newMonth.getMonth() + 1);
        }
        calendarState.currentDate = newMonth;
        calendarState.selectedDate = new Date(dayData.date);

        triggerPageTurn('forward');
        setTimeout(() => {
            loadCalendarData();
        }, 50);
    } else {
        // Same month - just update selection
        const direction = dayData.date > calendarState.selectedDate ? 'forward' : 'backward';
        calendarState.selectedDate = new Date(dayData.date);

        triggerPageTurn(direction);
        setTimeout(() => {
            updateMonthGridSelection();
            renderDayCard();
        }, 50);
    }
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
 * Check if two dates are the same day
 *
 * @param {Date} date1 - First date
 * @param {Date} date2 - Second date
 * @returns {boolean} - True if same day
 */
function isSameDay(date1, date2) {
    return date1.toDateString() === date2.toDateString();
}

/**
 * Jump to specific date
 *
 * @param {Date} date - Date to jump to
 */
export function jumpToDate(date) {
    calendarState.selectedDate = new Date(date);
    calendarState.currentDate = new Date(date);
    loadCalendarData();
}

/**
 * Refresh calendar data
 */
export function refreshCalendar() {
    loadCalendarData();
}

// Auto-initialize when module loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalendar);
} else {
    initCalendar();
}

// Export functions
export { initCalendar as default, loadCalendarData };
