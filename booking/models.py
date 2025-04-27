from django.db import models

# Create your models here.


class Booking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.check_in} to {self.check_out}"
    
