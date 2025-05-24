from django.test import TestCase
from datetime import date, timedelta
from booking.models import Booking, PricingConfig, PricingRule
from booking.utils import calculate_total_price

"""
Test dynamic pricing system:
- Base nightly rate from PricingConfig
- Date-specific overrides via PricingRule
- Total price calculation over booking span
"""

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ███ Test Setup
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

class DynamicPricingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set base nightly rate
        cls.base_rate = 100
        PricingConfig.objects.create(base_rate=cls.base_rate)

        # Create date range for test bookings
        cls.today = date.today()
        cls.check_in = cls.today + timedelta(days=1)
        cls.check_out = cls.today + timedelta(days=4)  # 3 nights

        # Add pricing overrides
        PricingRule.objects.create(date=cls.check_in, rate=120)               # day 1
        PricingRule.objects.create(date=cls.check_in + timedelta(days=2), rate=150)  # day 3

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ███ Unit Tests: Price Calculation
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

    def test_total_price_with_mixed_overrides(self):
        """
        Booking spans 3 nights:
        - Day 1: override 120
        - Day 2: base 100
        - Day 3: override 150
        Expected total: 120 + 100 + 150 = 370
        """
        total = calculate_total_price(self.check_in, self.check_out)
        self.assertEqual(total, 370)

    def test_total_price_all_base_rate(self):
        """No overrides in range: expect 3 * base_rate"""
        check_in = self.today + timedelta(days=10)
        check_out = check_in + timedelta(days=3)
        total = calculate_total_price(check_in, check_out)
        self.assertEqual(total, 3 * self.base_rate)

    def test_total_price_all_overrides(self):
        """All nights have specific overrides"""
        check_in = self.check_in
        check_out = check_in + timedelta(days=2)
        PricingRule.objects.create(date=check_in + timedelta(days=1), rate=130)
        expected = 120 + 130  # day 1 + day 2 overrides
        total = calculate_total_price(check_in, check_out)
        self.assertEqual(total, expected)

    def test_zero_night_booking_returns_zero(self):
        """Edge case: same check-in/check-out should be free"""
        total = calculate_total_price(self.check_in, self.check_in)
        self.assertEqual(total, 0)

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ███ Integration Test: Booking Model Price Field
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

    def test_booking_total_price_auto_set(self):
        """
        When a booking is created, total_price should be calculated
        automatically using overrides and base rate.
        """
        booking = Booking.objects.create(
            name="Test User",
            email="test@example.com",
            check_in=self.check_in,
            check_out=self.check_out,
            paid=True,
        )
        self.assertEqual(booking.total_price, 370)