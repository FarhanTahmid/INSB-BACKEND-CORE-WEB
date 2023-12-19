// Dummy events data for demonstration, this is the calendar event load function

console.log("hello")
const eventsData = {
    '2023-07-27': ['Event 1', 'Event 2'],
    '2023-07-23': ['Event 3'],
    '2023-07-15': ['hello event'],
    '2023-12-18' : ['test']
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
                
                eventsData[getFormattedDate(dayElement.date)].forEach(()=> {
                    const eventMark = document.createElement('div');
                    eventMark.classList.add('event-mark');
                    eventMark.style.width = '6px';
                    eventMark.style.height = '6px';
                    eventMark.style.borderRadius = '50%';
                    eventMark.style.backgroundColor = 'red';
                    eventMark.style.margin = '2px 1px';
                    eventMark.style.position = 'static';
                    dayElement.appendChild(eventMark);
                    
                })
               
                
                
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
        dayElement.addEventListener('click', () => showEventsForDate(date));
        return dayElement;
    }

    function showEventsForDate(date) {
        // console.log(data)
        const formattedDate = getFormattedDate(date);
        console.log(formattedDate)
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
        
        return date.toISOString('en-US').split('T')[0];
        // return date.toLocaleDateString('en-US');
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