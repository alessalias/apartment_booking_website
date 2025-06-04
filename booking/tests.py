"""
Test suite for the Booking app.

Covers:
- Booking model creation
- Booking form submission and validation
- Stripe checkout session integration
- Stripe webhook handling (successful and failure cases)
- Email confirmation after successful payment
- Business rules (past dates, overlapping bookings)
"""

from .forms import BookingForm
from .models import Booking, PricingConfig, PricingRule, AvailabilityConfig
from .utils import calculate_total_price, get_max_bookable_date
from datetime import date, timedelta
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import json
from unittest.mock import patch




# ----------------------------
# Test: Booking Model
# ----------------------------
class BookingModelTest(TestCase):
    def test_create_booking(self):
        """Test that a Booking instance can be created and stored."""
        booking = Booking.objects.create(
            name="John Doe",
            email="john@example.com",
            check_in=date(2025, 5, 1),
            check_out=date(2025, 5, 5),
        )

        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.name, "John Doe")
        self.assertEqual(booking.paid, False)


# ----------------------------
# Test: Booking Form Submission
# ----------------------------
class BookingFormSubmissionTest(TestCase):
    def setUp(self):
        self.url = reverse('book')
        self.check_in = timezone.now().date() + timedelta(days=5)
        self.check_out = self.check_in + timedelta(days=2)
        self.valid_data = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'check_in': self.check_in,
            'check_out': self.check_out,
        }

    @patch('booking.views.stripe.checkout.Session.create')
    def test_successful_booking_redirects_to_stripe(self, mock_stripe_session_create):
        """Submitting a valid form should redirect to Stripe checkout."""
        mock_session = mock_stripe_session_create.return_value
        mock_session.url = 'https://checkout.stripe.com/test_session'

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 303)
        self.assertIn('stripe.com', response['Location'])
        self.assertEqual(Booking.objects.count(), 0)  # No booking yet until webhook


# ----------------------------
# Test: Form Validation
# ----------------------------
class BookingFormValidationTest(TestCase):
    def setUp(self):
        self.url = reverse('book')

    def test_missing_name_fails(self):
        """Booking form should reject submissions without a name."""
        data = {
            'name': '',
            'email': 'no_name@example.com',
            'check_in': date.today() + timedelta(days=3),
            'check_out': date.today() + timedelta(days=5),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        self.assertEqual(Booking.objects.count(), 0)

    def test_past_check_in_date_fails(self):
        """Booking form should reject a check-in date in the past."""
        data = {
            'name': 'Bob',
            'email': 'bob@example.com',
            'check_in': date.today() - timedelta(days=2),
            'check_out': date.today() + timedelta(days=2),
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'Check-in date cannot be in the past.')
        self.assertEqual(Booking.objects.count(), 0)

    def test_overlapping_paid_booking_fails(self):
        """Form should reject dates that overlap with existing paid bookings."""
        Booking.objects.create(
            name='Existing Guest',
            email='existing@example.com',
            check_in=date.today() + timedelta(days=5),
            check_out=date.today() + timedelta(days=10),
            paid=True
        )

        data = {
            'name': 'New Guest',
            'email': 'new@example.com',
            'check_in': date.today() + timedelta(days=7),  # Overlaps
            'check_out': date.today() + timedelta(days=12),
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'These dates are already booked.')
        self.assertEqual(Booking.objects.count(), 1)  # Only original


# ----------------------------
# Test: Stripe Webhook Handling
# ----------------------------
class StripeWebhookTest(TestCase):
    def setUp(self):
        self.url = reverse('stripe-webhook')
        self.client = Client()
        self.check_in = date.today() + timedelta(days=5)
        self.check_out = self.check_in + timedelta(days=2)

    @patch('booking.views.stripe.Webhook.construct_event')
    def test_successful_checkout_session_creates_booking(self, mock_construct_event):
        """Webhook should create a booking when Stripe session completes."""
        metadata = {
            'name': 'Webhook User',
            'email': 'webhook@example.com',
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'total_price': 500,
        }
        event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'metadata': metadata}},
        }
        mock_construct_event.return_value = event

        response = self.client.post(
            self.url,
            data=json.dumps({}),  # Payload mocked
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='fake_signature'
        )

        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.name, 'Webhook User')
        self.assertTrue(booking.paid)

    @patch('booking.views.stripe.Webhook.construct_event')
    def test_webhook_fails_with_invalid_signature(self, mock_construct_event):
        """Invalid Stripe webhook signature should return 400."""
        mock_construct_event.side_effect = ValueError("Invalid payload")

        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )

        self.assertEqual(response.status_code, 400)


# ----------------------------
# Test: Email After Successful Payment
# ----------------------------
class EmailAfterPaymentTest(TestCase):
    @patch('booking.views.stripe.Webhook.construct_event')
    def test_email_is_sent_after_payment(self, mock_construct_event):
        """A confirmation email should be sent after a successful booking."""
        metadata = {
            'name': 'Email User',
            'email': 'emailuser@example.com',
            'check_in': (date.today() + timedelta(days=4)).isoformat(),
            'check_out': (date.today() + timedelta(days=7)).isoformat(),
            'total_price': 300,
        }
        event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'metadata': metadata}},
        }
        mock_construct_event.return_value = event

        self.client.post(
            reverse('stripe-webhook'),
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='fake'
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Booking Confirmation', mail.outbox[0].subject)
        self.assertIn('Thanks for your booking', mail.outbox[0].body)


# ----------------------------
# Test: Email Failure Handling
# ----------------------------
class WebhookEmailFailureTest(TestCase):
    @patch('booking.views.send_mail', side_effect=Exception("SMTP error"))
    @patch('booking.views.stripe.Webhook.construct_event')
    def test_email_failure_does_not_break_webhook(self, mock_construct_event, mock_send_mail):
        """If email sending fails, webhook should still succeed and booking should be created."""
        metadata = {
            'name': 'Fail Email',
            'email': 'fail@example.com',
            'check_in': (date.today() + timedelta(days=6)).isoformat(),
            'check_out': (date.today() + timedelta(days=8)).isoformat(),
            'total_price': 400,
        }
        event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'metadata': metadata}},
        }
        mock_construct_event.return_value = event

        response = self.client.post(
            reverse('stripe-webhook'),
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='fake'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.exists())


# ----------------------------
# Test: Webhook Integration (Invalid Signature)
# ----------------------------
class WebhookIntegrationTest(TestCase):
    def test_invalid_webhook_signature_returns_400(self):
        """Invalid Stripe webhook signature should return 400."""
        # Simulate Stripe webhook with invalid signature (no mocking)
        response = self.client.post(
            reverse('stripe-webhook'),
            data=json.dumps({"type": "checkout.session.completed"}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='obviously-wrong'  # Deliberately invalid
        )

        # Expecting 400 as the webhook signature is invalid
        self.assertEqual(response.status_code, 400)
        
        #This test simulates a real-world failure scenario where the webhook fails to validate due to a signature mismatch, helping catch misconfigured webhooks during deployment.



# ----------------------------
# Test: Availability Views (Calendar)
# ----------------------------
class AvailabilityViewTest(TestCase):
    def test_availability_html_renders_successfully(self):
        """GET /availability/ should return 200 and render the correct template."""
        response = self.client.get(reverse('availability'))

        # Check that the template renders successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/availability.html')

    def test_availability_json_returns_existing_bookings(self):
        """GET /availability/json/ should return JSON with paid bookings only."""
        Booking.objects.create(
            name="Calendar Test",
            email="calendar@test.com",
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=3),
            paid=True
        )

        response = self.client.get(reverse('availability_json'))
        data = response.json()

        # Filter only "Booked" events (i.e., actual bookings)
        booked_events = [event for event in data if event["title"] == "Booked"]

        # Expect exactly one "Booked" event
        self.assertEqual(len(booked_events), 1)
        self.assertEqual(booked_events[0]["title"], "Booked")

        # These tests verify both the frontend calendar view and the backend data JSON endpoint.



# ----------------------------
# Test: Webhook Error Handling (Missing Metadata)
# ----------------------------
@patch('booking.views.stripe.Webhook.construct_event')
def test_missing_metadata_gracefully_fails(mock_construct_event):
    """Webhook should ignore sessions with missing metadata without crashing."""
    event = {
        'type': 'checkout.session.completed',
        'data': {'object': {}},  # No metadata present
    }
    mock_construct_event.return_value = event

    response = Client().post(
        reverse('stripe-webhook'),
        data=json.dumps({}),  # Empty payload
        content_type='application/json',
        HTTP_STRIPE_SIGNATURE='fake'
    )

    # Should respond with 200 to Stripe to avoid retry, but do nothing
    assert response.status_code == 200
    assert Booking.objects.count() == 0

    # This test ensures robustness of the webhook handler when Stripe sends malformed or unexpected payloads, which is common in real-world edge cases.


# ----------------------------
# Test: Webhook Overlapping Paid Booking
# ----------------------------
@patch('booking.views.stripe.Webhook.construct_event')
def test_webhook_ignores_overlapping_paid_booking(mock_construct_event):
    """Webhook should not create booking if paid booking already exists for those dates."""
    # Create existing paid booking
    Booking.objects.create(
        name='Existing Guest',
        email='guest@demo.com',
        check_in=date.today() + timedelta(days=3),
        check_out=date.today() + timedelta(days=7),
        paid=True
    )

    # Create event with overlapping dates
    metadata = {
        'name': 'New Guest',
        'email': 'new@demo.com',
        'check_in': (date.today() + timedelta(days=4)).isoformat(),
        'check_out': (date.today() + timedelta(days=8)).isoformat(),
        'total_price': 500,
    }
    event = {
        'type': 'checkout.session.completed',
        'data': {'object': {'metadata': metadata}},
    }
    mock_construct_event.return_value = event

    response = Client().post(
        reverse('stripe-webhook'),
        data=json.dumps({}),
        content_type='application/json',
        HTTP_STRIPE_SIGNATURE='fake'
    )

    # Booking should not be created
    assert response.status_code == 200
    assert Booking.objects.count() == 1  # Only the original

    # This tests for overlapping booking scenarios that sneak past form validation but originate from webhook events.


"""
██████╗ ███████╗███████╗████████╗
██╔══██╗██╔════╝██╔════╝╚══██╔══╝
██████╔╝█████╗  █████╗     ██║   
██╔═══╝ ██╔══╝  ██╔══╝     ██║   
██║     ███████╗███████╗   ██║   
╚═╝     ╚══════╝╚══════╝   ╚═╝   
AVAILABILITY / BOOKING WINDOW TESTS
"""

class AvailabilityTests(TestCase):

    def setUp(self):
        self.today = date.today()
        self.config = AvailabilityConfig.objects.create(months_ahead=2)  # approx 60 days
        self.max_date = get_max_bookable_date()

    def test_max_bookable_date_calculation(self):
        expected_max = self.today + timedelta(days=60)
        self.assertEqual(self.max_date, expected_max)

    def test_booking_outside_window_rejected(self):
        form_data = {
            'name': 'John',
            'email': 'john@example.com',
            'check_in': self.max_date + timedelta(days=1),
            'check_out': self.max_date + timedelta(days=2),
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Check-in is too far in the future.", form.errors['__all__'])

    def test_booking_at_window_limit_is_valid(self):
        form_data = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'check_in': self.max_date,
            'check_out': self.max_date + timedelta(days=1),
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_booking_with_check_out_before_check_in(self):
        form_data = {
            'name': 'Foo',
            'email': 'foo@example.com',
            'check_in': self.today + timedelta(days=10),
            'check_out': self.today + timedelta(days=5),
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Check-out date must be after check-in date.", form.errors['__all__'])

"""
██████╗ ██████╗ ███████╗███████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝
██████╔╝██████╔╝█████╗  ███████╗
██╔═══╝ ██╔═══╝ ██╔══╝  ╚════██║
██║     ██║     ███████╗███████║
╚═╝     ╚═╝     ╚══════╝╚══════╝
PRICE CALCULATION TESTS
"""

class PricingTests(TestCase):

    def setUp(self):
        self.base_rate = 150
        PricingConfig.objects.create(base_rate=self.base_rate)
        self.today = date.today()

    def test_base_rate_applied_if_no_override(self):
        check_in = self.today
        check_out = self.today + timedelta(days=3)
        total = calculate_total_price(check_in, check_out)
        self.assertEqual(total, self.base_rate * 3)

    def test_override_price_applied_if_present(self):
        PricingRule.objects.create(date=self.today + timedelta(days=1), rate=200)
        check_in = self.today
        check_out = self.today + timedelta(days=3)
        total = calculate_total_price(check_in, check_out)
        # Only one override, others use base
        expected = self.base_rate + 200 + self.base_rate
        self.assertEqual(total, expected)


