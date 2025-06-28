from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from conference.models import Conference
from .models import Membership
from .forms import MembershipForm


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
