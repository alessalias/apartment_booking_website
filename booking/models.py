from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# Custom user model
class User(AbstractUser):
    # Add custom fields if any
    pass

class OwnerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Use settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name='owner_profile'
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Collaborator(models.Model):
    owner = models.ForeignKey(
        OwnerProfile,
        on_delete=models.CASCADE,
        related_name='collaborators'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Use settings.AUTH_USER_MODEL
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.email} (collaborator of {self.owner.name})"

class Booking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            from .utils import calculate_total_price  # the import is moved here in order to avoid circular import ⬅️ 
            self.total_price = calculate_total_price(self.check_in, self.check_out)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.check_in} to {self.check_out}"

class PricingRule(models.Model):
    date = models.DateField(unique=True)
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date}: {self.rate}€"

class PricingConfig(models.Model):
    base_rate = models.DecimalField(max_digits=6, decimal_places=2, default=120)
    # Optional: add FK to OwnerProfile or Property in future