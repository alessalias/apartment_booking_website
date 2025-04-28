# Navona Romantica Booking

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
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver

Before pushing changes, always run tests locally with:
python3 manage.py test

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
