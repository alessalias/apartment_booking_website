from .models import PricingRule, PricingConfig, AvailabilityConfig
from datetime import date, timedelta

DEFAULT_BASE_RATE = 150  # Fallback if no PricingConfig is set
DEFAULT_BOOKING_WINDOW_MONTHS = 3  # fallback if not configured


def calculate_total_price(check_in, check_out):
    current_date = check_in
    total = 0
    try:
        base_rate = PricingConfig.objects.first().base_rate
    except AttributeError:
        base_rate = DEFAULT_BASE_RATE  # Fallback default

    while current_date < check_out:
        rule = PricingRule.objects.filter(date=current_date).first()
        if rule:
            total += rule.rate
        else:
            total += base_rate
        current_date += timedelta(days=1)
    return total


def get_base_rate():
    """
    Returns the default nightly rate from PricingConfig,
    or a fallback value if not set.
    """
    config = PricingConfig.objects.first()
    return config.base_rate if config else DEFAULT_BASE_RATE  # fallback value


def get_override_price_for_date(target_date: date):
    """
    Returns the override price for a specific date if it exists,
    otherwise returns None.
    """
    rule = PricingRule.objects.filter(date=target_date).first()
    return rule.price if rule else None


def get_max_bookable_date():
    """
    Returns the latest date that guests can book, based on config.
    """
    config = AvailabilityConfig.objects.first()
    months = config.months_ahead if config else DEFAULT_BOOKING_WINDOW_MONTHS
    return date.today() + timedelta(days=months * 30)


def get_nightly_price(target_date: date):
    """
    Returns the nightly price for a given date,
    using override if it exists, otherwise base rate.
    """
    override = get_override_price_for_date(target_date)
    return override if override is not None else get_base_rate()