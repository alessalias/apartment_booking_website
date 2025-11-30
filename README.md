# Navona Romantica Booking

#### Video Demo: https://youtu.be/b_q5iXyLxxQ

[![Django CI](https://github.com/alessalias/navonaromantica/actions/workflows/django.yml/badge.svg)](https://github.com/alessalias/navonaromantica/actions/workflows/django.yml)
![Status](https://img.shields.io/badge/STATUS-WIP-yellow?style=for-the-badge)

Welcome to **Navona Romantica Booking**, a minimalist booking system built with Django!  
This app allows guests to book stays directly without needing third-party platforms.

---

## 🧠 Distinctiveness and Complexity

What you are viewing here is a live snapshot of a continuously evolving web application designed with the express purpose of solving a personal and business-critical need: enabling **direct online bookings** for a vacation rental property I manage. Ultimately, this system aims to **replace Airbnb** as the primary platform through which I engage with guests — giving me full control over availability, pricing, payments, and guest relationships.

### 🌍 Real-World Purpose and Motivation

At its core, this project solves a very real problem. Platforms like Airbnb offer convenience but at a steep price: high service fees, limited flexibility in terms of branding and guest experience, and a lack of ownership over the data and communication pipeline. By creating my own direct booking engine, I eliminate middlemen, retain a higher percentage of each booking, and gain the freedom to personalize the experience — all while building a long-term system I can adapt and expand as needed.

> This isn't just a portfolio project. It’s something I intend to deploy, maintain, and use every single day.

### 🧱 Architecture and Feature Complexity

This application is built with Django and integrates a number of interrelated components that mirror the functionality of professional booking platforms:

- **Full-featured booking engine** with check-in/check-out validation, real-time availability checks, dynamic pricing calculations, and payment processing.
- **Stripe integration** with secure checkout sessions, webhook handling, and email confirmations.
- **Custom calendar logic** using FullCalendar.js to display availability, pricing per night, and prevent overbooking.
- **Dynamic pricing system** allowing the property owner to set a base nightly rate and (soon) override prices on specific dates.
- **Availability window management** so the owner can restrict bookings to a specific range of dates (e.g., only allow bookings within the next 3 months).
- **Owner dashboard** that supports per-night rate editing, availability controls, and (in future iterations) user access management and reports.

All of this is designed within Django’s robust MVC framework, using reusable templates, test coverage for key logic paths, AJAX interactivity, and modular utilities.

### 🔄 Continuous Development and Future Scope

What you see here is not a finished product, but a **live cross-section** of a growing project. I am approaching this like a startup MVP — launching with a lean but powerful core, then layering in enhancements.

The current implementation focuses on owner functionality and core booking logic. Future milestones include:

- Guest-facing account features
- Review systems
- Google Calendar integration
- Multilingual support
- PWA (Progressive Web App) capabilities for mobile-first performance

### 💡 Why It’s Distinctive

Unlike cookie-cutter clones or tutorial-following projects, this application was designed **from first principles to solve a real need**. Every feature has been conceived, designed, implemented, and tested with the end goal of replacing Airbnb in my actual daily workflow.

It’s distinctive not just because of its functionality, but because of its **intentionality**: this project is deeply personal, business-driven, and meant to last.

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
