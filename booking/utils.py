from .models import PricingRule, PricingConfig
from datetime import timedelta


def calculate_total_price(check_in, check_out):
    current_date = check_in
    total = 0
    try:
        base_rate = PricingConfig.objects.first().base_rate
    except AttributeError:
        base_rate = 100  # Fallback default

    while current_date < check_out:
        rule = PricingRule.objects.filter(date=current_date).first()
        if rule:
            total += rule.rate
        else:
            total += base_rate
        current_date += timedelta(days=1)
    return total