from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from submissions.models import Submissions
from membership.models import Membership, Role
from .models import Review
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Q

@login_required
def chair_review_assignments(request):
    # Conferences where user is chair
    chair_memberships = Membership.objects.filter(user=request.user, role1=Role.CHAIR)
    chair_conferences = [m.conference for m in chair_memberships]

    # Get selected conference slug from GET param
    selected_slug = request.GET.get('conference')
    selected_conference = None
    submissions = Submissions.objects.none()

    if selected_slug:
        selected_conference = next((c for c in chair_conferences if c.slug == selected_slug), None)
        if selected_conference:
            submissions = Submissions.objects.filter(membership__conference=selected_conference).order_by('-submission_date')
    else:
        # If no filter, show all submissions across all chair conferences
        submissions = Submissions.objects.filter(membership__conference__in=chair_conferences).order_by('-submission_date')

    # TODO: Logic for assigning reviewers (probably via POST, or separate form/modal)
    # For now just list submissions and allow navigation

    context = {
        'chair_conferences': chair_conferences,
        'selected_conference': selected_conference,
        'submissions': submissions,
    }
    return render(request, 'review/chair_review_assignments.html', context)

@login_required
def reviewer_dashboard(request):
    # Reviews assigned to this reviewer and not submitted yet
    pending_reviews = Review.objects.filter(reviewer=request.user, is_submitted=False).select_related('submission').order_by('date_assigned')

    context = {
        'pending_reviews': pending_reviews,
    }
    return render(request, 'review/reviewer_dashboard.html', context)

@login_required
def submit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    submission = review.submission

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_submitted = True
            from django.utils import timezone
            review.date_reviewed = timezone.now()
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect('reviewer_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'submission': submission,
        'review': review,
    }
    return render(request, 'review/submit_review.html', context)

@login_required
def author_reviews(request):
    # Get all submissions by this user (including co-authored maybe)
    submissions = Submissions.objects.filter(
        Q(membership__user=request.user) | 
        Q(co_author1=request.user) | 
        Q(co_author2=request.user) | 
        Q(co_author3=request.user)
    )

    # Get all reviews for these submissions
    reviews = Review.objects.filter(submission__in=submissions).select_related('submission', 'reviewer').order_by('-date_reviewed')

    context = {
        'reviews': reviews,
    }
    return render(request, 'review/author_reviews.html', context)
