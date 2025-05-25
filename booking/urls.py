from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    path('', views.book_view, name='book'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path("availability/", views.availability_view, name="availability"),  # HTML view
    path("availability/json/", views.availability_json, name="availability_json"),  # JSON data
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/update-base-rate/', views.update_base_rate, name='update_base_rate'),
    path('owner/calendar/', views.owner_calendar, name='owner_calendar'),
    path('owner/booking-window/', views.manage_booking_window, name='manage_booking_window'),
    path('owner/calendar-data/', views.owner_calendar_data, name='calendar_data'),
    path('owner/update-price/', views.update_price, name='update_price'),
]