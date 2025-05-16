from datetime import date
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import BookingForm
import logging
import stripe
from smtplib import SMTPException
from .models import Booking


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

            # Calculate number of nights
            nights = (check_out - check_in).days
            total_amount = nights * nightly_rate * 100  # Stripe expects cents

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

# JSON data view
def availability_json(request):
    bookings = Booking.objects.all()
    events = []

    for booking in bookings:
        events.append({
            "title": "Booked",
            "start": booking.check_in.isoformat(),
            "end": booking.check_out.isoformat(),
            "color": "red"
        })

    return JsonResponse(events, safe=False)