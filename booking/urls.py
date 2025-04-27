from django.urls import path
from . import views


urlpatterns = [
    path('', views.book_view, name='book'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
]