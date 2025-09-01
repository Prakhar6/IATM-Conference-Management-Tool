from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:slug>/', views.payment_checkout, name='payment_checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('status/<slug:slug>/', views.payment_status, name='payment_status'),
    path('webhook/', views.paypal_webhook, name='paypal_webhook'),
]
