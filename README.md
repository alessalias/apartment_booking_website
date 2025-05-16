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
- SQLite database for easy development setup

---

## 🛠 Technology Stack

- **Backend**: Python, Django
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
- **GitHub Actions** — Continuous Integration (CI)

---

## 🛠️ Project Structure

```plaintext
navonaromantica/
│
├── booking/               # Booking app
│   ├── migrations/        # Django migrations
│   ├── templates/         # HTML templates
│   ├── static/            # Static files (CSS, JS)
│   ├── forms.py           # Booking form
│   ├── models.py          # Database models
│   ├── views.py           # App views
│   └── tests.py           # Unit tests
│
├── navonaromantica/       # Project settings
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation (this file)
```

---

## ✨ Future Improvements

- Add calendar view for availability
- Allow cancellations/modifications
- Admin dashboard for managing bookings
- Internationalization (multi-language support)
- Deployment on a cloud server (coming soon!)

---

