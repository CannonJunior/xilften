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

    // Setup drag-and-drop for day card
    setupDragAndDrop();

    // Load and render initial calendar
    loadCalendarData();

    console.log('✅ Calendar sidebar initialized');
}

/**
 * Setup drag-and-drop functionality for adding movies to calendar
 */
function setupDragAndDrop() {
    const dayCard = document.getElementById('day-detail-card');
    const dayContainer = document.querySelector('.day-detail-container');

    console.log('📅 Setting up drag-and-drop');
    console.log('📅 Day card element:', dayCard);
    console.log('📅 Day container element:', dayContainer);

    if (!dayContainer) {
        console.error('❌ Day container not found! Cannot setup drag-and-drop');
        return;
    }

    console.log('✅ Day container found, adding event listeners');

    // Prevent default drag behavior
    dayContainer.addEventListener('dragenter', (event) => {
        console.log('📅 DRAG ENTER - over day container');
        event.preventDefault();
    });

    dayContainer.addEventListener('dragover', (event) => {
        console.log('📅 DRAG OVER - over day container');
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';

        if (!dayContainer.classList.contains('drag-over')) {
            console.log('📅 Adding drag-over class');
            dayContainer.classList.add('drag-over');
        }
    });

    dayContainer.addEventListener('dragleave', (event) => {
        console.log('📅 DRAG LEAVE - left day container', event.target);
        if (event.target === dayContainer) {
            console.log('📅 Removing drag-over class');
            dayContainer.classList.remove('drag-over');
        }
    });

    dayContainer.addEventListener('drop', async (event) => {
        console.log('📅 DROP EVENT - Item dropped!');
        event.preventDefault();
        dayContainer.classList.remove('drag-over');

        const mediaId = event.dataTransfer.getData('mediaId');
        const mediaTitle = event.dataTransfer.getData('mediaTitle');

        console.log('📅 Retrieved from dataTransfer - mediaId:', mediaId, 'mediaTitle:', mediaTitle);

        if (!mediaId) {
            console.error('❌ No media ID found in drag data');
            console.log('📅 Available dataTransfer types:', event.dataTransfer.types);
            return;
        }

        console.log(`📅 Dropped movie: ${mediaTitle} (${mediaId}) on ${calendarState.selectedDate.toDateString()}`);

        // Create calendar event for this movie
        await createMovieEvent(mediaId, mediaTitle, calendarState.selectedDate);
    });

    console.log('✅ Drag-and-drop event listeners added successfully');
}

/**
 * Create a movie event on the calendar
 *
 * @param {string} mediaId - Media UUID
 * @param {string} mediaTitle - Media title
 * @param {Date} date - Event date
 */
async function createMovieEvent(mediaId, mediaTitle, date) {
    console.log('📅 createMovieEvent called');
    console.log('📅 Parameters - mediaId:', mediaId, 'mediaTitle:', mediaTitle, 'date:', date);

    try {
        const eventData = {
            title: `Watch: ${mediaTitle}`,
            event_type: 'watch',
            event_date: date.toISOString().split('T')[0], // YYYY-MM-DD format
            media_id: mediaId
        };

        console.log('📅 Creating calendar event with data:', eventData);

        const response = await api.createCalendarEvent(eventData);

        console.log('📅 API response:', response);

        if (response && response.id) {
            console.log('✅ Calendar event created successfully!');
            console.log('✅ Event details:', response);

            // Reload calendar data to show the new event
            console.log('📅 Reloading calendar data...');
            await loadCalendarData();

            // Re-render the current day card to show the new event
            console.log('📅 Re-rendering day card...');
            renderDayCard();
            console.log('✅ Calendar updated!');
        } else {
            console.error('❌ Failed to create calendar event:', response);
        }
    } catch (error) {
        console.error('❌ Error creating calendar event:', error);
        console.error('❌ Error stack:', error.stack);
    }
}

/**
 * Delete calendar event
 *
 * @param {string} eventId - Event UUID
 */
async function deleteEvent(eventId) {
    console.log('🗑️ Deleting event:', eventId);

    try {
        const response = await api.deleteCalendarEvent(eventId);
        console.log('🗑️ Delete response:', response);

        // Reload calendar data to remove the deleted event
        await loadCalendarData();

        // Re-render the current day card
        renderDayCard();

        console.log('✅ Event deleted successfully!');
    } catch (error) {
        console.error('❌ Error deleting event:', error);
    }
}

/**
 * Setup mousewheel scrolling for day navigation
 * Enhanced with 3x animation speed and momentum-based hard scroll detection
 */
function setupMousewheelScrolling() {
    const sidebar = document.getElementById('calendar-sidebar');
    if (!sidebar) return;

    let scrollTimeout;
    let lastScrollTime = 0;

    sidebar.addEventListener('wheel', (event) => {
        event.preventDefault();

        // Don't scroll if animation is in progress
        if (calendarState.isAnimating) {
            return;
        }

        // Calculate scroll velocity for momentum detection
        const currentTime = Date.now();
        const timeDelta = currentTime - lastScrollTime;
        lastScrollTime = currentTime;

        // Detect hard scroll based on deltaY magnitude and timing
        const absDelta = Math.abs(event.deltaY);
        const isHardScroll = absDelta > 100 || (timeDelta < 50 && absDelta > 50);

        // Determine scroll direction (always 1 day at a time)
        const direction = Math.sign(event.deltaY);

        // Calculate animation speed based on scroll intensity
        let animationSpeed;
        if (isHardScroll) {
            // Hard scroll: 10x faster animation (rapid page flipping)
            animationSpeed = 30; // 30ms per day = ~33 days/second
        } else {
            // Normal scroll: 3x faster than default
            // Default would be ~300ms, so 3x = 100ms per day
            animationSpeed = 100;
        }

        // Change selected date by 1 day
        const newDate = new Date(calendarState.selectedDate);
        newDate.setDate(newDate.getDate() + direction);

        // Check if we crossed a month boundary
        const crossedMonth = newDate.getMonth() !== calendarState.selectedDate.getMonth();

        calendarState.selectedDate = newDate;

        if (crossedMonth) {
            calendarState.currentDate = new Date(newDate);
        }

        // Trigger page turn animation with speed parameter
        const animDirection = direction > 0 ? 'forward' : 'backward';
        triggerPageTurn(animDirection, animationSpeed);

        // Debounce the rendering based on animation speed
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            if (crossedMonth) {
                renderMonthGrid();
            } else {
                updateMonthGridSelection();
            }
            renderDayCard();
        }, animationSpeed * 0.5); // Render halfway through animation
    }, { passive: false });
}

/**
 * Trigger page turn animation
 *
 * @param {string} direction - 'forward' or 'backward'
 * @param {number} speed - Animation duration in milliseconds (default: 300ms)
 */
function triggerPageTurn(direction, speed = 300) {
    const dayCard = document.getElementById('day-detail-card');
    if (!dayCard) return;

    calendarState.isAnimating = true;

    // Remove any existing animation classes
    dayCard.classList.remove('page-turn-forward', 'page-turn-backward');

    // Set custom animation duration via CSS variable
    dayCard.style.setProperty('--page-turn-duration', `${speed}ms`);

    // Force reflow to restart animation
    void dayCard.offsetWidth;

    // Add appropriate animation class
    const className = direction === 'forward' ? 'page-turn-forward' : 'page-turn-backward';
    dayCard.classList.add(className);

    // Remove animation class after animation completes
    setTimeout(() => {
        dayCard.classList.remove(className);
        calendarState.isAnimating = false;
    }, speed);
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
            calendarState.events = response || [];
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

            // Add delete button
            const deleteButton = eventDiv
                .append('div')
                .attr('class', 'day-detail-event-delete')
                .attr('title', 'Delete event')
                .text('🗑️')
                .on('click', async (e) => {
                    e.stopPropagation();
                    await deleteEvent(event.id);
                });
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
