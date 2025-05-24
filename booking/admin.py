from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Booking, OwnerProfile, Collaborator, PricingRule, PricingConfig

User = get_user_model()

admin.site.register(User)
admin.site.register(Booking)
admin.site.register(OwnerProfile)
admin.site.register(Collaborator)
admin.site.register(PricingRule)
admin.site.register(PricingConfig)