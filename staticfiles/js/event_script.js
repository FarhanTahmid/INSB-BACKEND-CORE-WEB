// Dummy events data for demonstration, this is the calendar event load function
const eventsData = {
    '2023-09-10': ['Event 1', 'Event 2'],
    '2023-07-23': ['Event 3'],
    '2023-07-20': ['Spac event'],
};

document.addEventListener('DOMContentLoaded', () => {
    const calendarContainer = document.querySelector('.calendar');
    const daysContainer = document.querySelector('.days');
    const monthYear = document.querySelector('.month-year');
    const eventBox = document.querySelector('.event-box');
    const selectedDateText = document.querySelector('.selected-date');
    const eventsList = document.querySelector('.events-list');

    let currentDate = new Date();
    renderCalendar(currentDate);

    function renderCalendar(date) {
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']; // Day abbreviations
        const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        const prevMonthLastDay = new Date(date.getFullYear(), date.getMonth(), 0);
        const daysInMonth = lastDay.getDate();
        const daysInPrevMonth = prevMonthLastDay.getDate();
        const startDay = firstDay.getDay();
        const endDay = lastDay.getDay();
        const prevMonthDays = startDay === 0 ? 6 : startDay - 1;
        const nextMonthDays = endDay === 0 ? 0 : 7 - endDay;

        daysContainer.innerHTML = '';

        // Display previous month days
        for (let i = prevMonthDays; i > 0; i--) {
            const day = daysInPrevMonth - i + 1;
            const dayElement = createDayElement(new Date(date.getFullYear(), date.getMonth() - 1, day));
            dayElement.classList.add('prev-month');
            daysContainer.appendChild(dayElement);
        }

        // Display current month days
        for (let i = 1; i <= daysInMonth; i++) {
            const dayElement = createDayElement(new Date(date.getFullYear(), date.getMonth(), i));
            if (eventsData.hasOwnProperty(getFormattedDate(dayElement.date))) {
                const eventMark = document.createElement('div');
                eventMark.classList.add('event-mark');
                dayElement.appendChild(eventMark);
            }
            daysContainer.appendChild(dayElement);
        }

        // Display next month days
        for (let i = 1; i <= nextMonthDays; i++) {
            const dayElement = createDayElement(new Date(date.getFullYear(), date.getMonth() + 1, i));
            dayElement.classList.add('next-month');
            daysContainer.appendChild(dayElement);
        }

        monthYear.textContent = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }

    function createDayElement(date) {
        const dayElement = document.createElement('div');
        dayElement.classList.add('day');
        dayElement.textContent = date.getDate();
        dayElement.date = date;
        dayElement.addEventListener('click', () => showEventsForDate((date));
        return dayElement;
    }

    function showEventsForDate(date) {
        const formattedDate = getFormattedDate(date);
        selectedDateText.textContent = formattedDate;
        const eventsForDate = eventsData[formattedDate] || [];
        eventsList.innerHTML = '';
        if (eventsForDate.length > 0) {
            eventBox.style.display = 'block';
            eventBox.classList.add('show');
            eventsForDate.forEach((event) => {
                const eventItem = document.createElement('li');
                eventItem.textContent = event;
                eventsList.appendChild(eventItem);
            });
        } else {
            eventBox.style.display = 'none';
            eventBox.classList.remove('show');
        }
    }

    function getFormattedDate(date) {
        return date.toISOString().split('T')[0];
    }

    document.querySelector('.prev-btn').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    document.querySelector('.next-btn').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });
});

function eventFilterFunction() {
    var input, filter, box, eventName, i, txtValue;
    input = document.getElementById("eventFilter");
    filter = input.value.toUpperCase();
    box = document.getElementsByClassName("event_box");
    for (i = 0; i < box.length; i++) {
        eventName = box[i].getElementsByClassName("event_name")[0];
        if (eventName) {
            txtValue = eventName.textContent || eventName.innerText;
            console.log('Name: ', txtValue)
            if (txtValue.toUpperCase().indexOf(filter) > -1) {

                box[i].style.display = "block";
            } else {
                box[i].style.display = "none";
            }
        }
    }
}