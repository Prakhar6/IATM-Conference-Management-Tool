import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.core.mail import send_mass_mail
from django.conf import settings
from conference.models import Conference, Payment
from .models import Membership, Role
from .forms import MembershipForm
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def networking_hub(request, slug):
    """Attendee directory for networking (paid registrants only)."""
    conference = get_object_or_404(Conference, slug=slug)

    # Only paid registrants can access
    if not Membership.objects.filter(user=request.user, conference=conference, is_paid=True).exists():
        messages.error(request, "You must be a paid registrant to access the networking hub.")
        return redirect('conference_detail', slug=slug)

    attendees = Membership.objects.filter(conference=conference, is_paid=True).select_related('user')

    query = request.GET.get('q', '')
    if query:
        attendees = attendees.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__organization__icontains=query) |
            Q(user__country__icontains=query)
        )

    context = {
        'conference': conference,
        'attendees': attendees,
        'query': query,
    }
    return render(request, 'membership/networking_hub.html', context)


@login_required
def group_registration(request, slug):
    """Register and pay for multiple attendees at once."""
    conference = get_object_or_404(Conference, slug=slug)
    from conference.models import RegistrationTier

    tiers = RegistrationTier.objects.filter(conference=conference, is_active=True)

    if request.method == 'POST':
        emails_raw = request.POST.get('emails', '')
        emails = [e.strip() for e in emails_raw.split('\n') if e.strip()]

        if not emails:
            messages.error(request, "Please enter at least one email address.")
            return redirect('group_registration', slug=slug)

        from accounts.models import CustomUser
        registered = []
        errors = []

        for email in emails:
            try:
                user = CustomUser.objects.get(email=email)
                if Membership.objects.filter(user=user, conference=conference).exists():
                    errors.append(f"{email} is already registered.")
                else:
                    Membership.objects.create(
                        user=user,
                        conference=conference,
                        role1='Author',
                        is_paid=False,
                    )
                    registered.append(email)
            except CustomUser.DoesNotExist:
                errors.append(f"{email} - no account found.")

        if registered:
            messages.success(request, f"Registered {len(registered)} attendee(s): {', '.join(registered)}")
        if errors:
            messages.warning(request, "Issues: " + "; ".join(errors))

        return redirect('group_registration', slug=slug)

    memberships = Membership.objects.filter(conference=conference).select_related('user').order_by('-created_at')[:20]

    context = {
        'conference': conference,
        'tiers': tiers,
        'recent_memberships': memberships,
    }
    return render(request, 'membership/group_registration.html', context)


@login_required
def register_for_conference(request, slug):
    conference = get_object_or_404(Conference, slug=slug)

    # Check existing membership
    if Membership.objects.filter(user=request.user, conference=conference).exists():
        messages.info(request, "You have already registered for this conference.")
        return redirect('conference_detail', slug=slug)

    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            Membership.objects.create(
                user=request.user,
                conference=conference,
                role1=form.cleaned_data['role1'],
                role2=form.cleaned_data['role2']
            )
            messages.success(request, "Registration submitted successfully!")
            return redirect('conference_detail', slug=slug)
    else:
        form = MembershipForm()

    return render(request, 'membership/register.html', {
        'conference': conference,
        'form': form
    })


@staff_member_required
def admin_conference_dashboard_view(request, slug):
    conference = get_object_or_404(Conference, slug=slug)
    memberships = Membership.objects.filter(conference=conference).select_related('user').exclude(user__is_staff=True)

    if request.method == 'POST':
        member_id = request.POST.get('membership_id')
        role1 = request.POST.get('role1')
        role2 = request.POST.get('role2')
        # Removed action/status update

        membership = Membership.objects.get(id=member_id)
        membership.role1 = role1
        membership.role2 = role2

        membership.save()
        return redirect('admin_conference_dashboard', slug=slug)

    # No status-based filtering here anymore
    return render(request, 'conference/admin_dashboard.html', {
        'conference': conference,
        'memberships': memberships,  # all memberships passed to template
        'Role': Role,
    })


@staff_member_required
def admin_analytics_view(request, slug):
    """Real-time analytics: revenue, registrations, geography."""
    conference = get_object_or_404(Conference, slug=slug)
    memberships = Membership.objects.filter(conference=conference)

    # Registration stats
    total_registrations = memberships.count()
    paid_registrations = memberships.filter(is_paid=True).count()
    unpaid_registrations = total_registrations - paid_registrations

    # Revenue
    payments = Payment.objects.filter(conference=conference, status='completed')
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0

    # Role breakdown
    authors = memberships.filter(Q(role1='Author') | Q(role2='Author')).count()
    reviewers = memberships.filter(Q(role1='Reviewer') | Q(role2='Reviewer')).count()
    chairs = memberships.filter(Q(role1='Chair') | Q(role2='Chair')).count()

    # Geography (country breakdown)
    country_stats = memberships.values('user__country').annotate(
        count=Count('id')
    ).order_by('-count')[:15]

    # Occupation breakdown
    occupation_stats = memberships.values('user__occupation').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'conference': conference,
        'total_registrations': total_registrations,
        'paid_registrations': paid_registrations,
        'unpaid_registrations': unpaid_registrations,
        'total_revenue': total_revenue,
        'authors': authors,
        'reviewers': reviewers,
        'chairs': chairs,
        'country_stats': country_stats,
        'occupation_stats': occupation_stats,
    }
    return render(request, 'membership/admin_analytics.html', context)


@staff_member_required
def export_attendees_csv(request, slug):
    """Export attendee list as CSV."""
    conference = get_object_or_404(Conference, slug=slug)
    memberships = Membership.objects.filter(conference=conference).select_related('user')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{conference.slug}_attendees.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email', 'First Name', 'Last Name', 'Organization', 'Country', 'Phone', 'Occupation', 'Role 1', 'Role 2', 'Paid', 'Registration Date'])

    for m in memberships:
        writer.writerow([
            m.user.email,
            m.user.first_name,
            m.user.last_name,
            m.user.organization,
            m.user.country,
            m.user.phone,
            m.user.get_occupation_display(),
            m.role1,
            m.role2,
            'Yes' if m.is_paid else 'No',
            m.created_at.strftime('%Y-%m-%d'),
        ])

    return response


@staff_member_required
def export_financials_csv(request, slug):
    """Export financial report as CSV."""
    conference = get_object_or_404(Conference, slug=slug)
    payments = Payment.objects.filter(conference=conference).select_related('user', 'tier')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{conference.slug}_financials.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Email', 'Name', 'Tier', 'Amount', 'Currency', 'Status', 'PayPal Order ID', 'Date'])

    for p in payments:
        writer.writerow([
            f'INV-{p.id:06d}',
            p.user.email,
            p.user.get_full_name(),
            p.tier.name if p.tier else 'N/A',
            p.amount,
            p.currency,
            p.get_status_display(),
            p.paypal_order_id or '',
            p.created_at.strftime('%Y-%m-%d'),
        ])

    return response


@login_required
def download_badge(request, membership_id):
    """Download printable name badge PDF with QR code."""
    membership = get_object_or_404(Membership, id=membership_id)

    if membership.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to download this badge.")
        return redirect('user_dashboard')

    if not membership.is_paid:
        messages.error(request, "Badge is only available for paid registrations.")
        return redirect('user_dashboard')

    from .badge import generate_badge_pdf
    buffer = generate_badge_pdf(membership)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="badge_{membership.user.first_name}_{membership.conference.slug}.pdf"'
    return response


@login_required
def download_qr_ticket(request, membership_id):
    """Download QR code ticket as PNG image."""
    membership = get_object_or_404(Membership, id=membership_id)

    if membership.user != request.user and not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect('user_dashboard')

    if not membership.is_paid:
        messages.error(request, "QR ticket is only available for paid registrations.")
        return redirect('user_dashboard')

    from .badge import generate_qr_code
    qr_data = f"IATM|{membership.user.email}|{membership.conference.slug}|{membership.id}"
    qr_buf = generate_qr_code(qr_data)

    response = HttpResponse(qr_buf.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="ticket_{membership.conference.slug}.png"'
    return response


@staff_member_required
def bulk_email_view(request, slug):
    """Send bulk HTML emails to segmented attendee lists."""
    conference = get_object_or_404(Conference, slug=slug)
    memberships = Membership.objects.filter(conference=conference).select_related('user')

    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')
        segment = request.POST.get('segment', 'all')

        if not subject or not body:
            messages.error(request, "Subject and body are required.")
            return redirect('bulk_email', slug=slug)

        # Segment recipients
        recipients = memberships
        if segment == 'paid':
            recipients = recipients.filter(is_paid=True)
        elif segment == 'unpaid':
            recipients = recipients.filter(is_paid=False)
        elif segment == 'authors':
            recipients = recipients.filter(Q(role1='Author') | Q(role2='Author'))
        elif segment == 'reviewers':
            recipients = recipients.filter(Q(role1='Reviewer') | Q(role2='Reviewer'))

        email_list = []
        for m in recipients:
            email_list.append((
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [m.user.email],
            ))

        if email_list:
            try:
                send_mass_mail(email_list, fail_silently=False)
                messages.success(request, f"Email sent to {len(email_list)} recipient(s).")
            except Exception as e:
                messages.error(request, f"Failed to send emails: {str(e)}")
        else:
            messages.warning(request, "No recipients matched the selected segment.")

        return redirect('bulk_email', slug=slug)

    segment_counts = {
        'all': memberships.count(),
        'paid': memberships.filter(is_paid=True).count(),
        'unpaid': memberships.filter(is_paid=False).count(),
        'authors': memberships.filter(Q(role1='Author') | Q(role2='Author')).count(),
        'reviewers': memberships.filter(Q(role1='Reviewer') | Q(role2='Reviewer')).count(),
    }

    context = {
        'conference': conference,
        'segment_counts': segment_counts,
    }
    return render(request, 'membership/bulk_email.html', context)
