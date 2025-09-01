from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Conference
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def conference_list_view(request):
    conferences = Conference.objects.all()
    return render(request, 'conference/conference_list.html', {'conferences': conferences})

@login_required
def conference_detail_view(request, slug):
    conference = get_object_or_404(Conference, slug=slug)
    return render(request, 'conference/conference_detail.html', {'conference': conference})

@login_required
def payment_checkout(request, slug):
    """Payment checkout - shows payment form and processes payment"""
    conference = get_object_or_404(Conference, slug=slug)
    
    # Check if user already has a membership for this conference
    from membership.models import Membership
    try:
        membership = Membership.objects.get(user=request.user, conference=conference)
        if membership.is_paid:
            messages.info(request, f"You already have access to {conference.conference_name}.")
            return redirect('conference_detail', slug=slug)
    except Membership.DoesNotExist:
        # Create membership if it doesn't exist
        membership = Membership.objects.create(
            user=request.user,
            conference=conference,
            is_paid=False
        )
    
    # Calculate price based on user occupation
    if request.user.occupation in ['student_undergraduate', 'student_graduate']:
        amount = 50.00  # Student price
        price_type = "Student"
    else:
        amount = 100.00  # Regular price
        price_type = "Regular"
    
    if request.method == 'POST':
        # Process PayPal payment
        try:
            from paypal_checkout_sdk.services import OrdersService
            from paypal_checkout_sdk.models.orders import CreateOrderRequest
            from paypal_config import get_paypal_client
            
            # Create PayPal order request data
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": f"conf_{conference.id}_user_{request.user.id}",
                    "description": f"{conference.conference_name} - {price_type} Registration",
                    "amount": {
                        "currency_code": "USD",
                        "value": str(amount)
                    }
                }],
                "application_context": {
                    "return_url": request.build_absolute_uri(reverse('payment_success', kwargs={'slug': slug})),
                    "cancel_url": request.build_absolute_uri(reverse('payment_cancel', kwargs={'slug': slug})),
                    "brand_name": "IATM Conference",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "shipping_preference": "NO_SHIPPING"
                }
            }
            
            # Create the order request
            request_paypal = CreateOrderRequest(**order_data)
            
            # Execute the request using OrdersService
            client = get_paypal_client()
            orders_service = OrdersService(client)
            response = orders_service.create_order(request_paypal)
            
            # Store order ID in session for verification
            request.session['paypal_order_id'] = response.id
            request.session['conference_slug'] = slug
            
            # Redirect to PayPal for payment
            # Extract the approve link URL from the HttpUrl object
            if hasattr(response, 'links') and response.links:
                for link in response.links:
                    if hasattr(link, 'rel') and link.rel == "approve":
                        if hasattr(link, 'href'):
                            # Convert HttpUrl to string and redirect
                            paypal_url = str(link.href)
                            return redirect(paypal_url)
            
            # Fallback: construct PayPal URL manually
            paypal_url = f"https://www.paypal.com/checkoutnow?token={response.id}"
            return redirect(paypal_url)
            
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('conference_detail', slug=slug)
    
    # Show payment form
    context = {
        'conference': conference,
        'amount': amount,
        'price_type': price_type,
        'membership': membership
    }
    return render(request, 'conference/payment_checkout.html', context)

@login_required
def payment_success(request, slug):
    """Handle successful PayPal payment"""
    conference = get_object_or_404(Conference, slug=slug)
    
    # Get PayPal order ID from session
    paypal_order_id = request.session.get('paypal_order_id')
    conference_slug = request.session.get('conference_slug')
    
    if not paypal_order_id or conference_slug != slug:
        messages.error(request, "Invalid payment session")
        return redirect('conference_detail', slug=slug)
    
    try:
        from paypal_checkout_sdk.services import OrdersService
        from paypal_config import get_paypal_client
        
        # Capture the payment using OrdersService
        client = get_paypal_client()
        orders_service = OrdersService(client)
        response = orders_service.capture_order(paypal_order_id)
        
        if response.status == "COMPLETED":
            # Update membership to paid
            from membership.models import Membership
            membership = Membership.objects.get(user=request.user, conference=conference)
            membership.is_paid = True
            membership.save()
            
            # Clear session data
            if 'paypal_order_id' in request.session:
                del request.session['paypal_order_id']
            if 'conference_slug' in request.session:
                del request.session['conference_slug']
            
            messages.success(request, f"Payment successful! You now have access to {conference.conference_name}")
            return redirect('conference_detail', slug=slug)
        else:
            messages.error(request, "Payment was not completed successfully")
            return redirect('conference_detail', slug=slug)
            
    except Exception as e:
        messages.error(request, f"Payment verification error: {str(e)}")
        return redirect('conference_detail', slug=slug)

@login_required
def payment_cancel(request, slug):
    """Handle cancelled PayPal payment"""
    conference = get_object_or_404(Conference, slug=slug)
    
    # Clear session data
    if 'paypal_order_id' in request.session:
        del request.session['paypal_order_id']
    if 'conference_slug' in request.session:
        del request.session['conference_slug']
    
    messages.info(request, "Payment was cancelled. You can try again anytime.")
    return redirect('conference_detail', slug=slug)
