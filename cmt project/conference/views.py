from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Conference, Payment, RegistrationTier
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from submissions.emails import send_registration_confirmation

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
    
    # Get available registration tiers
    tiers = RegistrationTier.objects.filter(conference=conference, is_active=True)
    is_member = request.user.iatm_membership

    # Determine pricing: use tiers if configured, else fallback to legacy pricing
    if tiers.exists():
        # Build tier pricing info for display
        tier_pricing = []
        for tier in tiers:
            current_price = tier.get_current_price(is_member=is_member)
            tier_pricing.append({
                'tier': tier,
                'price': current_price,
                'original_price': tier.price,
                'is_discounted': current_price < float(tier.price),
            })
    else:
        # Legacy fallback: Student $50 / Regular $100
        tier_pricing = None

    if request.method == 'POST':
        # Determine amount from selected tier or legacy pricing
        selected_tier = None
        if tiers.exists():
            tier_id = request.POST.get('tier_id')
            if tier_id:
                selected_tier = get_object_or_404(RegistrationTier, id=tier_id, conference=conference)
                amount = selected_tier.get_current_price(is_member=is_member)
                price_type = selected_tier.name
            else:
                messages.error(request, "Please select a registration tier.")
                return redirect('payment_checkout', slug=slug)
        else:
            # Legacy pricing
            if request.user.occupation in ['student_undergraduate', 'student_graduate']:
                amount = 50.00
                price_type = "Student"
            else:
                amount = 100.00
                price_type = "Regular"

        # Process PayPal payment
        try:
            from paypal_checkout_sdk.services import OrdersService
            from paypal_checkout_sdk.models.orders import CreateOrderRequest
            from paypal_config import get_paypal_client

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

            request_paypal = CreateOrderRequest(**order_data)
            client = get_paypal_client()
            orders_service = OrdersService(client)
            response = orders_service.create_order(request_paypal)

            # Create Payment record
            Payment.objects.create(
                user=request.user,
                conference=conference,
                tier=selected_tier,
                amount=amount,
                paypal_order_id=response.id,
                status='pending'
            )

            request.session['paypal_order_id'] = response.id
            request.session['conference_slug'] = slug

            if hasattr(response, 'links') and response.links:
                for link in response.links:
                    if hasattr(link, 'rel') and link.rel == "approve":
                        if hasattr(link, 'href'):
                            return redirect(str(link.href))

            return redirect(f"https://www.paypal.com/checkoutnow?token={response.id}")

        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('conference_detail', slug=slug)

    # Show payment form
    context = {
        'conference': conference,
        'membership': membership,
        'tier_pricing': tier_pricing,
        'is_member': is_member,
        'is_early_bird': conference.is_early_bird,
    }

    # Legacy fallback context
    if not tier_pricing:
        if request.user.occupation in ['student_undergraduate', 'student_graduate']:
            context['amount'] = 50.00
            context['price_type'] = "Student"
        else:
            context['amount'] = 100.00
            context['price_type'] = "Regular"

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

            # Update Payment record
            try:
                payment = Payment.objects.get(paypal_order_id=paypal_order_id)
                payment.status = 'completed'
                # Extract capture ID if available
                if hasattr(response, 'purchase_units') and response.purchase_units:
                    pu = response.purchase_units[0]
                    if hasattr(pu, 'payments') and hasattr(pu.payments, 'captures') and pu.payments.captures:
                        payment.paypal_payment_id = pu.payments.captures[0].id
                payment.save()
            except Payment.DoesNotExist:
                pass

            # Clear session data
            if 'paypal_order_id' in request.session:
                del request.session['paypal_order_id']
            if 'conference_slug' in request.session:
                del request.session['conference_slug']

            send_registration_confirmation(request.user, conference, membership, request=request)
            messages.success(request, f"Payment successful! You now have access to {conference.conference_name}")
            return redirect('conference_detail', slug=slug)
        else:
            # Mark payment as failed
            try:
                payment = Payment.objects.get(paypal_order_id=paypal_order_id)
                payment.status = 'failed'
                payment.save()
            except Payment.DoesNotExist:
                pass
            messages.error(request, "Payment was not completed successfully")
            return redirect('conference_detail', slug=slug)
            
    except Exception as e:
        messages.error(request, f"Payment verification error: {str(e)}")
        return redirect('conference_detail', slug=slug)

@login_required
def payment_cancel(request, slug):
    """Handle cancelled PayPal payment"""
    conference = get_object_or_404(Conference, slug=slug)

    # Mark Payment as cancelled
    paypal_order_id = request.session.get('paypal_order_id')
    if paypal_order_id:
        try:
            payment = Payment.objects.get(paypal_order_id=paypal_order_id)
            payment.status = 'cancelled'
            payment.save()
        except Payment.DoesNotExist:
            pass

    # Clear session data
    if 'paypal_order_id' in request.session:
        del request.session['paypal_order_id']
    if 'conference_slug' in request.session:
        del request.session['conference_slug']

    messages.info(request, "Payment was cancelled. You can try again anytime.")
    return redirect('conference_detail', slug=slug)


@login_required
def user_dashboard(request):
    """User dashboard showing registrations, payments, submissions, and personalized schedule."""
    from membership.models import Membership
    from submissions.models import Submissions
    from schedule.models import Session
    from django.db.models import Q
    from django.utils import timezone

    memberships = Membership.objects.filter(user=request.user).select_related('conference')
    payments = Payment.objects.filter(user=request.user, status='completed').select_related('conference', 'tier')
    submissions = Submissions.objects.filter(
        Q(membership__user=request.user) |
        Q(co_author1=request.user) |
        Q(co_author2=request.user) |
        Q(co_author3=request.user)
    ).select_related('membership__conference', 'track').distinct()

    # Personalized schedule: upcoming sessions for conferences the user is registered (paid) for
    paid_conferences = memberships.filter(is_paid=True).values_list('conference_id', flat=True)
    upcoming_sessions = Session.objects.filter(
        conference_id__in=paid_conferences,
        is_published=True,
        end_time__gte=timezone.now(),
    ).select_related('conference', 'track').prefetch_related('speakers').order_by('start_time')[:10]

    # Conferences eligible for certificate (past conferences where user attended sessions)
    from schedule.models import Attendance
    past_paid_memberships = memberships.filter(
        is_paid=True,
        conference__end_date__lt=timezone.now().date(),
    )
    certificate_memberships = []
    for m in past_paid_memberships:
        attendance_count = Attendance.objects.filter(user=request.user, session__conference=m.conference).count()
        if attendance_count > 0:
            certificate_memberships.append({'membership': m, 'sessions_attended': attendance_count})

    context = {
        'memberships': memberships,
        'payments': payments,
        'submissions': submissions,
        'upcoming_sessions': upcoming_sessions,
        'certificate_memberships': certificate_memberships,
    }
    return render(request, 'conference/user_dashboard.html', context)


@login_required
def download_invoice(request, payment_id):
    """Download PDF invoice for a completed payment."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user, status='completed')

    from .invoice import generate_invoice_pdf
    buffer = generate_invoice_pdf(payment)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="IATM_Invoice_{payment.id:06d}.pdf"'
    return response


@login_required
def download_certificate(request, membership_id):
    """Download attendance certificate PDF for a completed conference."""
    from membership.models import Membership
    from schedule.models import Attendance

    membership = get_object_or_404(Membership, id=membership_id, user=request.user, is_paid=True)

    # Conference must be over
    from django.utils import timezone
    if membership.conference.end_date >= timezone.now().date():
        messages.error(request, "Certificates are available after the conference ends.")
        return redirect('user_dashboard')

    # User must have attended at least one session
    attendance_count = Attendance.objects.filter(
        user=request.user, session__conference=membership.conference
    ).count()
    if attendance_count == 0:
        messages.error(request, "No session attendance recorded for this conference.")
        return redirect('user_dashboard')

    from .certificate import generate_certificate_pdf
    buffer = generate_certificate_pdf(request.user, membership.conference, attendance_count)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f"IATM_Certificate_{membership.conference.slug}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
