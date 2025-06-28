from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from conference.models import Conference
from .models import Membership, Role, Status
from .forms import MembershipForm
from django.contrib.admin.views.decorators import staff_member_required


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
            messages.success(request, "Registration submitted successfully! Awaiting approval.")
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
        action = request.POST.get('action')  # 'approve', 'deny', 'revert'

        membership = Membership.objects.get(id=member_id)
        membership.role1 = role1
        membership.role2 = role2

        if action == 'approve':
            membership.status = Status.ACCEPTED
        elif action == 'deny':
            membership.status = Status.REJECTED
        elif action == 'revert':
            membership.status = Status.PENDING

        membership.save()
        return redirect('admin_conference_dashboard', slug=slug)

    pending = memberships.filter(status=Status.PENDING)
    accepted = memberships.filter(status=Status.ACCEPTED)

    return render(request, 'conference/admin_dashboard.html', {
        'conference': conference,
        'pending_memberships': pending,
        'accepted_memberships': accepted,
        'Role': Role,
    })