let calendar;  // <-- Declare outside
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');
  if (calendarEl) {
    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      height: 'auto',
      events: '/owner/calendar-data/',
      dateClick: function(info) {
        const dateStr = info.dateStr;
        const event = calendar.getEvents().find(e => e.startStr === dateStr);

        document.getElementById('modal-date').value = dateStr;
        document.getElementById('modal-price').value = event?.extendedProps.price ?? '';
        new bootstrap.Modal(document.getElementById('priceModal')).show();
      },
      eventContent: function(arg) {
        let price = arg.event.extendedProps.price;
        let isBooked = arg.event.extendedProps.booked;
        return {
          html: `<div style="font-size:0.85em">${price ? '€' + price : ''} ${isBooked ? '<span class="badge bg-danger">Booked</span>' : ''}</div>`
        };
      }
    });
    calendar.render();
  }

  // Form submission logic
  const priceForm = document.getElementById('priceForm');
  if (priceForm) {
    priceForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const date = document.getElementById('modal-date').value;
      const price = document.getElementById('modal-price').value;
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      const response = await fetch('/owner/update-price/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date, price })
      });

      const data = await response.json();
      if (data.success) {
        calendar.refetchEvents();
        bootstrap.Modal.getInstance(document.getElementById('priceModal')).hide();
      } else {
        alert('Failed to save');
      }
    });
  }
});