from .models import Booking, AvailabilityConfig
from .utils import get_max_bookable_date
from datetime import timedelta
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        latest_allowed = get_max_bookable_date()

        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out date must be after check-in date.")
        
        # Only validate if check_in is provided and valid
        if check_in and check_in > latest_allowed:
            raise ValidationError("Check-in is too far in the future.")

        # Only validate if check_out is provided and valid
        if check_out and check_out > latest_allowed + timedelta(days=1):
            raise ValidationError("Check-out is too far in the future.")


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords must match.")
        return cleaned_data


class AvailabilityConfigForm(forms.ModelForm):
    class Meta:
        model = AvailabilityConfig
        fields = ['months_ahead']
        widgets = {
            'months_ahead': forms.NumberInput(attrs={'min': 1, 'max': 24, 'class': 'form-control'})
        }