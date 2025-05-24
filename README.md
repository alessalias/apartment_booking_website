# Navona Romantica Booking

#### Video Demo: https://youtu.be/b_q5iXyLxxQ

[![Django CI](https://github.com/alessalias/navonaromantica/actions/workflows/django.yml/badge.svg)](https://github.com/alessalias/navonaromantica/actions/workflows/django.yml)

Welcome to **Navona Romantica Booking**, a minimalist booking system built with Django!  
This app allows guests to book stays directly without needing third-party platforms.

---

## 🚀 Features

- Simple and elegant booking form
- Stripe integration for secure payments
- Automatic booking conflict detection
- Email confirmation system
- Webhook integration for post-payment booking creation
- Robust test suite (Test-Driven Development)
- CI/CD with GitHub Actions for automated testing
- Dynamic nightly pricing (base rate + per-date overrides)
- Availability window: restrict bookings to a defined range (e.g., 3 months)
- FullCalendar integration on frontend to display booked nights and nightly rates

---

## 🛠 Technology Stack

- **Backend**: Python, Django
- **Frontend Calendar**: FullCalendar.io (JavaScript)
- **AJAX**: For dynamic pricing updates
- **Payments**: Stripe Checkout
- **Database**: SQLite (default Django setup)
- **Testing**: Django `TestCase`, GitHub Actions
- **Deployment**: (Coming soon!)

---

## 🧰 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/alessalias/navonaromantica.git
cd navonaromantica
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python3 manage.py migrate
```

### 5. Run the development server

```bash
python3 manage.py runserver
```

---

## 🧪 Running Tests

Before pushing changes, always run tests locally:

```bash
python3 manage.py test
```

GitHub Actions will also automatically run these tests on every push.

---

## ⚙️ Technologies Used

- **Django** — Web Framework
- **Stripe** — Payment Gateway
- **SQLite** — Default lightweight database
- **FullCalendar.io** — Client-side interactive calendar
- **AJAX** — Frontend-backend communication
- **GitHub Actions** — Continuous Integration (CI)

---

## 🛠️ Project Structure

```plaintext
navonaromantica/
│
├── booking/                   # Main booking app
│   ├── migrations/            # Django migrations
│   ├── templates/booking/     # Client-facing booking templates
│   ├── templates/owner/       # Owner dashboard templates
│   ├── templates/registration/# Auth templates (login/register/logout)
│   ├── admin.py               # Admin panel config
│   ├── apps.py                # App config
│   ├── decorators.py          # Custom view decorators
│   ├── forms.py               # Forms for booking
│   ├── models.py              # Data models
│   ├── urls.py                # App-level routing
│   ├── views.py               # Booking views
│   ├── utils.py               # Utility functions (e.g. pricing)
│   ├── tests.py               # Core tests
│   ├── test_utils.py          # Tests for utility functions
│   └── test_dynamic_pricing.py # Tests for dynamic pricing behavior
│
├── config/                    # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/                    # Static files (CSS, JS)
│   └── styles.css
│
├── staticfiles/               # Collected static files for deployment
├── db.sqlite3                 # SQLite development database
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation (this file)
```

---

## ✨ Future Improvements

- Owner dashboard with editable pricing calendar
- Collaborator/invite system for co-management
- Visual blocked-out dates beyond availability window
- Add calendar view for availability (✔️ Done)
- Allow cancellations/modifications
- Internationalization (multi-language support)
- Deployment on a cloud server (coming soon!)

---