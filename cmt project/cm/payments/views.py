import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from conference.models import Conference
# from membership.models import Membership, Role
from .models import Payment
import os

# PayPal configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', 'your_paypal_client_secret')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

def get_paypal_base_url():
    if PAYPAL_MODE == 'live':
        return 'https://api-m.paypal.com'
    return 'https://api-m.sandbox.paypal.com'

def get_paypal_access_token():
    """Get PayPal access token"""
    url = f"{get_paypal_base_url()}/v1/oauth2/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials',
    }
    
    response = requests.post(
        url, 
        headers=headers, 
        data=data,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    return None

@login_required
def payment_checkout(request, slug):
    """Initiate PayPal payment"""
    conference = get_object_or_404(Conference, slug=slug)
    
    # Check if user already has a payment
    existing_payment = Payment.objects.filter(user=request.user, conference=conference).first()
    
    # Calculate price based on user occupation
    if request.user.occupation in ['student_undergraduate', 'student_graduate']:
        amount = 50.00  # Student price
        price_type = "Student"
    else:
        amount = 100.00  # Regular price
        price_type = "Regular"
    
    # Create or update payment record
    if existing_payment:
        payment = existing_payment
        payment.amount = amount
        payment.save()
    else:
        payment = Payment.objects.create(
            user=request.user,
            conference=conference,
            amount=amount,
            status='pending'
        )
    
    # Create PayPal order
    access_token = get_paypal_access_token()
    if not access_token:
        messages.error(request, "Payment service temporarily unavailable.")
        return redirect('conference_detail', slug=slug)
    
    paypal_order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": f"conf_{conference.id}_user_{request.user.id}",
            "description": f"Conference Registration: {conference.conference_name}",
            "amount": {
                "currency_code": "USD",
                "value": str(amount)
            }
        }],
        "application_context": {
            "return_url": request.build_absolute_uri(reverse('payment_success')),
            "cancel_url": request.build_absolute_uri(reverse('payment_cancelled')),
            "brand_name": "IATM Conference",
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW"
        }
    }
    
    url = f"{get_paypal_base_url()}/v2/checkout/orders"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url, headers=headers, json=paypal_order_data)
    
    if response.status_code == 201:
        order_data = response.json()
        paypal_order_id = order_data['id']
        
        # Update payment record with PayPal order ID
        payment.paypal_order_id = paypal_order_id
        payment.save()
        
        # Get PayPal checkout URL
        checkout_url = None
        for link in order_data['links']:
            if link['rel'] == 'approve':
                checkout_url = link['href']
                break
        
        if checkout_url:
            return redirect(checkout_url)
        else:
            messages.error(request, "Unable to redirect to payment.")
            return redirect('conference_detail', slug=slug)
    else:
        messages.error(request, "Unable to create payment order.")
        return redirect('conference_detail', slug=slug)

@login_required
def payment_success(request):
    """Handle successful PayPal payment"""
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, "Payment verification failed.")
        return redirect('conference_list')
    
    # Get payment record
    try:
        payment = Payment.objects.get(paypal_order_id=token)
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('conference_list')
    
    # Capture the payment
    access_token = get_paypal_access_token()
    if not access_token:
        messages.error(request, "Payment verification failed.")
        return redirect('conference_detail', slug=payment.conference.slug)
    
    url = f"{get_paypal_base_url()}/v2/checkout/orders/{token}/capture"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        capture_data = response.json()
        
        # Update payment status
        payment.status = 'completed'
        payment.paypal_payment_id = capture_data['purchase_units'][0]['payments']['captures'][0]['id']
        payment.save()
        
        # For now, we'll just use the Payment model to track access
        # The membership system can be enhanced later
        pass
        
        messages.success(request, f"Payment successful! You now have access to {payment.conference.conference_name}.")
        return redirect('conference_detail', slug=payment.conference.slug)
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, "Payment verification failed.")
        return redirect('conference_detail', slug=payment.conference.slug)

@login_required
def payment_cancelled(request):
    """Handle cancelled PayPal payment"""
    messages.info(request, "Payment was cancelled.")
    return redirect('conference_list')

@login_required
def payment_status(request, slug):
    """Show payment status for a specific conference"""
    conference = get_object_or_404(Conference, slug=slug)
    payment = Payment.objects.filter(user=request.user, conference=conference).first()
    
    return render(request, 'payments/payment_status.html', {
        'payment': payment,
        'conference': conference
    })

@csrf_exempt
def paypal_webhook(request):
    """Handle PayPal webhooks for payment status updates"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    # Verify webhook signature (implement proper verification in production)
    webhook_data = json.loads(request.body)
    
    # Handle different webhook events
    event_type = webhook_data.get('event_type')
    
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        # Payment completed
        payment_id = webhook_data['resource']['id']
        try:
            payment = Payment.objects.get(paypal_payment_id=payment_id)
            payment.status = 'completed'
            payment.save()
            
            # For now, we'll just use the Payment model to track access
            # The membership system can be enhanced later
            pass
                
        except Payment.DoesNotExist:
            pass
    
    elif event_type == 'PAYMENT.CAPTURE.DENIED':
        # Payment denied
        payment_id = webhook_data['resource']['id']
        try:
            payment = Payment.objects.get(paypal_payment_id=payment_id)
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    return HttpResponse(status=200)
