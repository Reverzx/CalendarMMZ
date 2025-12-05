let currentDate = new Date();
let currentEditingEventId = null;
let events = [];

const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

document.addEventListener('DOMContentLoaded', function() {
    loadEvents();
    renderCalendar();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    document.getElementById('addEventBtn').addEventListener('click', () => {
        currentEditingEventId = null;
        document.getElementById('modalTitle').textContent = 'Новое событие';
        document.getElementById('eventForm').reset();
        document.getElementById('eventModal').style.display = 'block';
    });

    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('eventModal').style.display = 'none';
    });

    document.getElementById('cancelBtn').addEventListener('click', () => {
        document.getElementById('eventModal').style.display = 'none';
    });

    document.getElementById('eventForm').addEventListener('submit', handleFormSubmit);

    window.addEventListener('click', (e) => {
        const modal = document.getElementById('eventModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        events = await response.json();
        renderCalendar();
        renderEventsList();
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function renderCalendar() {
    const calendar = document.getElementById('calendar');
    calendar.innerHTML = '';

    document.getElementById('currentMonth').textContent =
        `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;

    dayNames.forEach(day => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'day-header';
        dayHeader.textContent = day;
        calendar.appendChild(dayHeader);
    });

    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    let dayOfWeek = firstDay.getDay();
    dayOfWeek = dayOfWeek === 0 ? 6 : dayOfWeek - 1;

    for (let i = 0; i < dayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        calendar.appendChild(emptyDay);
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';

        const currentDayDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
        currentDayDate.setHours(0, 0, 0, 0);

        if (currentDayDate.getTime() === today.getTime()) {
            dayElement.classList.add('today');
        }

        const hasEvent = events.some(event => {
            const eventDate = new Date(event.start_time);
            return eventDate.getDate() === day &&
                   eventDate.getMonth() === currentDate.getMonth() &&
                   eventDate.getFullYear() === currentDate.getFullYear();
        });

        if (hasEvent) {
            dayElement.classList.add('has-event');
        }

        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = day;
        dayElement.appendChild(dayNumber);

        dayElement.addEventListener('click', () => {
            const selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            openEventModalForDate(selectedDate);
        });

        calendar.appendChild(dayElement);
    }
}

function openEventModalForDate(date) {
    currentEditingEventId = null;
    document.getElementById('modalTitle').textContent = 'Новое событие';
    document.getElementById('eventForm').reset();

    const dateStr = date.toISOString().split('T')[0];
    document.getElementById('eventStartTime').value = `${dateStr}T09:00`;
    document.getElementById('eventEndTime').value = `${dateStr}T10:00`;

    document.getElementById('eventModal').style.display = 'block';
}

function renderEventsList() {
    const eventsList = document.getElementById('eventsList');
    eventsList.innerHTML = '';

    const sortedEvents = [...events].sort((a, b) =>
        new Date(a.start_time) - new Date(b.start_time)
    );

    sortedEvents.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';

        const startDate = new Date(event.start_time);
        const endDate = new Date(event.end_time);

        eventItem.innerHTML = `
            <h4>${event.title}</h4>
            <p>${event.description || 'Без описания'}</p>
            <p><strong>Начало:</strong> ${formatDateTime(startDate)}</p>
            <p><strong>Конец:</strong> ${formatDateTime(endDate)}</p>
            <div class="event-actions">
                <button class="btn-edit" onclick="editEvent(${event.id})">Редактировать</button>
                <button class="btn-delete" onclick="deleteEvent(${event.id})">Удалить</button>
            </div>
        `;

        eventsList.appendChild(eventItem);
    });
}

function formatDateTime(date) {
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const eventData = {
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDescription').value,
        start_time: new Date(document.getElementById('eventStartTime').value).toISOString(),
        end_time: new Date(document.getElementById('eventEndTime').value).toISOString()
    };

    try {
        let response;
        if (currentEditingEventId) {
            response = await fetch(`/api/events/${currentEditingEventId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventData)
            });
        } else {
            response = await fetch('/api/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventData)
            });
        }

        if (response.ok) {
            document.getElementById('eventModal').style.display = 'none';
            loadEvents();
        } else {
            alert('Ошибка при сохранении события');
        }
    } catch (error) {
        console.error('Error saving event:', error);
        alert('Ошибка при сохранении события');
    }
}

async function editEvent(eventId) {
    const event = events.find(e => e.id === eventId);
    if (!event) return;

    currentEditingEventId = eventId;
    document.getElementById('modalTitle').textContent = 'Редактировать событие';
    document.getElementById('eventTitle').value = event.title;
    document.getElementById('eventDescription').value = event.description || '';

    const startDate = new Date(event.start_time);
    const endDate = new Date(event.end_time);

    document.getElementById('eventStartTime').value = formatDateTimeLocal(startDate);
    document.getElementById('eventEndTime').value = formatDateTimeLocal(endDate);

    document.getElementById('eventModal').style.display = 'block';
}

async function deleteEvent(eventId) {
    if (!confirm('Вы уверены, что хотите удалить это событие?')) {
        return;
    }

    try {
        const response = await fetch(`/api/events/${eventId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadEvents();
        } else {
            alert('Ошибка при удалении события');
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        alert('Ошибка при удалении события');
    }
}

function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}
