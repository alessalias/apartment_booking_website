document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('booking-window-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.ok ? response.json() : Promise.reject(response))
        .then(data => {
            showFeedback("Booking window updated successfully ✅", "success");
        })
        .catch(error => {
            showFeedback("An error occurred while saving ❌", "danger");
        });
    });

    function showFeedback(message, type) {
        const el = document.getElementById('feedback-message');
        el.className = `alert alert-${type}`;
        el.innerText = message;
        el.style.display = 'block';
    }
});