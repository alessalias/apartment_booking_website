from .decorators import owner_required
from .forms import BookingForm, RegisterForm, AvailabilityConfigForm
from .models import Booking, PricingRule, PricingConfig, OwnerProfile, AvailabilityConfig
from .utils import calculate_total_price, get_base_rate, get_override_price_for_date, get_nightly_price
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django import forms
import logging
from smtplib import SMTPException
import stripe

User = get_user_model()


stripe.api_key = settings.STRIPE_SECRET_KEY
nightly_rate = settings.NIGHTLY_RATE
logger = logging.getLogger(__name__)


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


def book_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid(): 
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            # Check for past dates
            if check_in < date.today():
                return render(request, 'booking/book.html', {
                    'form': form,
                    'error': 'Check-in date cannot be in the past.',
                })

            # Check for overlapping paid bookings only
            overlapping = Booking.objects.filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in),
                paid=True
            )
            if overlapping.exists():
                return render(request, 'booking/book.html', {
                    'form': form,
                    'error': 'These dates are already booked.',
                })

            total_amount = int(float(calculate_total_price(check_in, check_out)) * 100) # Stripe expects cents as integers

            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'Booking for {name}',
                        },
                        'unit_amount': total_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.DOMAIN + '/success/',
                cancel_url=settings.DOMAIN + '/cancel/',
                metadata={
                    'name': name,
                    'email': email,
                    'check_in': check_in.isoformat(),
                    'check_out': check_out.isoformat(),
                    'total_price': total_amount / 100,
                }
            )
            return HttpResponseSeeOther(session.url)
        else:
            # Form is invalid: redisplay with errors
            return render(request, 'booking/book.html', {'form': form})
    else:
        form = BookingForm()

    return render(request, 'booking/book.html', {'form': form})

def payment_success(request):
    return render(request, 'booking/success.html')

def payment_cancel(request):
    return render(request, 'booking/cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session['metadata']

        try:
            with transaction.atomic():
                check_in = date.fromisoformat(metadata['check_in'])
                check_out = date.fromisoformat(metadata['check_out'])

                overlapping = Booking.objects.select_for_update().filter(
                    Q(check_in__lt=check_out) & Q(check_out__gt=check_in),
                    paid=True
                )
                if overlapping.exists():
                    return JsonResponse({'error': 'Dates already booked'}, status=409)

                booking = Booking.objects.create(
                    name=metadata['name'],
                    email=metadata['email'],
                    check_in=check_in,
                    check_out=check_out,
                    total_price=metadata.get('total_price', 0),
                    paid=True
                )

        except Exception as e:
            logger.error(f"Webhook booking creation failed: {e}")
            return JsonResponse({'error': 'Booking creation failed'}, status=500)

        try:
            send_mail(
                subject='Booking Confirmation - Navona Romantica',
                message=f"Hi {booking.name},\n\nThanks for your booking from {booking.check_in} to {booking.check_out}.\nWe look forward to welcoming you!",
                from_email=None,
                recipient_list=[booking.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Booking created but email sending failed: {e}")

        return JsonResponse({'status': 'success'})

    return HttpResponse(status=200)



# HTML view
def availability_view(request):
    return render(request, "booking/availability.html")

def availability_json(request):
    today = date.today()

    # Get availability window
    availability_config = AvailabilityConfig.objects.first()
    months_ahead = availability_config.months_ahead if availability_config else 3
    max_date = today + timedelta(days=months_ahead * 30)

    # Bookings
    bookings = Booking.objects.all()
    events = []

    for booking in bookings:
        events.append({
            "title": "Booked",
            "start": booking.check_in.isoformat(),
            "end": booking.check_out.isoformat(),
            "color": "red"
        })

    # Pricing rules
    pricing_rules = PricingRule.objects.filter(date__range=(today, max_date))
    pricing_dict = {pr.date: pr.price for pr in pricing_rules}
    base_rate = get_base_rate()

    # Add price for each available day
    current = today
    while current <= max_date:
        if not any(b.check_in <= current < b.check_out for b in bookings):  # Skip if already booked
            price = pricing_dict.get(current, base_rate)
            events.append({
                "title": f"€{price}",
                "start": current.isoformat(),
                "allDay": True,
                "color": "#d1e7dd",
                "textColor": "#0f5132"
            })
        current += timedelta(days=1)

    return JsonResponse(events, safe=False)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()

                # Attach owner profile by default for now
                OwnerProfile.objects.create(user=user, name=form.cleaned_data['name'])

                login(request, user)
                return redirect('owner_dashboard')

            except IntegrityError:
                form.add_error('username', 'Username already taken.')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("owner_dashboard")
        else:
            return render(request, "registration/login.html", {
                "message": "Invalid username or password."
            })
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@owner_required
def owner_dashboard(request):
    today = now().date()
    upcoming_bookings = Booking.objects.filter(check_out__gte=today).order_by('check_in')
    base_price_obj = PricingConfig.objects.first()
    base_rate = base_price_obj.base_rate if base_price_obj else None

    context = {
        'bookings': upcoming_bookings,
        'base_rate': base_rate,
    }
    return render(request, 'owner/dashboard.html', context)


@require_POST
@owner_required
def update_base_rate(request):
    new_rate = request.POST.get('base_rate')
    try:
        rate_decimal = Decimal(new_rate)
        config, _ = PricingConfig.objects.get_or_create(pk=1)
        config.base_rate = rate_decimal
        config.save()
    except (InvalidOperation, TypeError):
        pass  # Optional: add error feedback

    return redirect('owner_dashboard')


@owner_required
def owner_calendar(request):
    return render(request, 'owner/calendar.html')


@owner_required
def manage_booking_window(request):
    config = AvailabilityConfig.objects.first()

    if request.method == 'POST':
        form = AvailabilityConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()

            # If it's an AJAX request, return JSON instead of redirecting
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Booking window updated successfully."})

            messages.success(request, "Booking window updated successfully.")
            return redirect('manage_booking_window')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "errors": form.errors,
                }, status=400)
    else:
        form = AvailabilityConfigForm(instance=config)

    return render(request, 'owner/manage_booking_window.html', {
        'form': form,
    })



def owner_calendar_data(request):
    # Show current + next month (adjust as needed)
    today = date.today()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=62))

    events = []

    d = start_date
    while d <= end_date:
        price = get_nightly_price(d)
        is_booked = Booking.objects.filter(check_in__lte=d, check_out__gt=d, paid=True).exists()
        events.append({
            'title': f"€{price}" if price else '',
            'start': d.isoformat(),
            'allDay': True,
            'extendedProps': {
                'price': price,
                'booked': is_booked,
            },
            'color': '#f0f0f0' if not is_booked else '#f8d7da',
            'textColor': '#000'
        })
        d += timedelta(days=1)

    return JsonResponse(events, safe=False)


@csrf_exempt
def update_price(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
            price = int(data['price'])

            rule, created = PricingRule.objects.update_or_create(
                date=date_obj,
                defaults={'price': price}
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})