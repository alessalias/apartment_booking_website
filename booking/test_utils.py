from django.test import TestCase
from datetime import date, timedelta
from booking.models import PricingRule, PricingConfig
from booking.utils import calculate_total_price, DEFAULT_BASE_RATE  # Import the fallback rate constant

class CalculateTotalPriceTest(TestCase):
    def setUp(self):
        # Set base rate
        PricingConfig.objects.create(base_rate=150)

        # Custom rules
        PricingRule.objects.create(date=date.today() + timedelta(days=1), rate=200)
        PricingRule.objects.create(date=date.today() + timedelta(days=2), rate=180)

    def test_total_price_with_base_and_custom_rates(self):
        """
        Total price should sum up custom rates where present and fallback to base rate.
        """
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=4)

        total = calculate_total_price(check_in, check_out)
        expected_total = 200 + 180 + 150  # day 1, 2, 3

        self.assertEqual(total, expected_total)

    def test_total_price_all_default_base_rate(self):
        """
        Should apply base rate for all nights if no custom rates exist.
        """
        PricingRule.objects.all().delete()
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=4)

        total = calculate_total_price(check_in, check_out)
        expected_total = 3 * 150

        self.assertEqual(total, expected_total)

    
    def test_total_price_with_missing_pricing_config(self):
        """
        Should fallback to DEFAULT_BASE_RATE if no PricingConfig exists.
        """
        PricingConfig.objects.all().delete()
        PricingRule.objects.all().delete()

        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        total = calculate_total_price(check_in, check_out)
        expected_total = 2 * DEFAULT_BASE_RATE  # Use the constant, not hardcoded value

        self.assertEqual(total, expected_total)