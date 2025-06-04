function updateNightlyRate(date, price) {
  fetch('/your-update-url/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // remove if using csrf_exempt
      },
      body: JSON.stringify({ date: date, price: price })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          // Optionally show success toast
          console.log('Price updated successfully.');
      } else {
          // Show the friendly error message
          alert(data.error);  // Replace with toast/modal for better UX
      }
  })
  .catch(() => {
      alert('Network error. Please try again.');
  });
}