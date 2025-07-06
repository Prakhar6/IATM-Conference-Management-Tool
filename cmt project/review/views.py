from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, ReviewerAssignment
from .forms import ReviewForm
from submissions.models import Submissions
from membership.models import Membership, Role
from django.db.models import Q

@login_required
def review_list(request):
    # Get user's memberships where they are a reviewer
    reviewer_memberships = Membership.objects.filter(
        user=request.user,
        role1=Role.REVIEWER
    )
    
    # Get submissions that have been assigned to this reviewer
    submissions_to_review = Submissions.objects.filter(
        reviewer_assignments__reviewer__in=reviewer_memberships
    ).exclude(
        review__membership__user=request.user  # Exclude already reviewed submissions
    ).order_by('-submission_date')
    
    # Get reviews done by the user
    completed_reviews = Review.objects.filter(
        membership__user=request.user
    ).order_by('-date_reviewed')
    
    return render(request, 'review/review_list.html', {
        'submissions_to_review': submissions_to_review,
        'completed_reviews': completed_reviews,
    })

@login_required
def create_review(request, submission_id):
    submission = get_object_or_404(Submissions, pk=submission_id)
    
    # Check if user is a reviewer for this conference and has been assigned this submission
    try:
        reviewer_membership = Membership.objects.get(
            user=request.user,
            conference=submission.membership.conference,
            role1=Role.REVIEWER
        )
        # Check if the reviewer has been assigned this submission
        if not ReviewerAssignment.objects.filter(reviewer=reviewer_membership, submission=submission).exists():
            messages.error(request, "You have not been assigned to review this submission")
            return redirect('review_list')
    except Membership.DoesNotExist:
        messages.error(request, "You are not authorized to review submissions for this conference")
        return redirect('review_list')
    
    # Check if user hasn't already reviewed this submission
    if Review.objects.filter(membership=reviewer_membership, submission=submission).exists():
        messages.error(request, "You have already reviewed this submission")
        return redirect('review_list')
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.membership = reviewer_membership
            review.submission = submission
            review.save()
            messages.success(request, "Review submitted successfully")
            return redirect('review_list')
    else:
        form = ReviewForm()
    
    return render(request, 'review/create_review.html', {
        'form': form,
        'submission': submission,
    })

@login_required
def manage_reviewers(request, submission_id):
    submission = get_object_or_404(Submissions, pk=submission_id)
    
    # Check if user is a chair for this conference
    try:
        chair_membership = Membership.objects.get(
            user=request.user,
            conference=submission.membership.conference,
            role1=Role.CHAIR
        )
    except Membership.DoesNotExist:
        messages.error(request, "You are not authorized to manage reviewers for this conference")
        return redirect('conference_detail', slug=submission.membership.conference.slug)
    
    # Get all reviewers for this conference
    available_reviewers = Membership.objects.filter(
        conference=submission.membership.conference,
        role1=Role.REVIEWER
    ).exclude(
        user=submission.membership.user  # Exclude the author
    ).exclude(
        assigned_reviews__submission=submission  # Exclude already assigned reviewers
    )
    
    # Get currently assigned reviewers
    assigned_reviewers = Membership.objects.filter(
        assigned_reviews__submission=submission
    )
    
    if request.method == "POST":
        reviewer_id = request.POST.get('reviewer_id')
        action = request.POST.get('action')
        
        if action == 'assign':
            reviewer = get_object_or_404(Membership, id=reviewer_id)
            ReviewerAssignment.objects.create(
                reviewer=reviewer,
                submission=submission,
                assigned_by=chair_membership
            )
            messages.success(request, f"Reviewer {reviewer.user.username} assigned successfully")
        
        elif action == 'unassign':
            ReviewerAssignment.objects.filter(
                reviewer_id=reviewer_id,
                submission=submission
            ).delete()
            messages.success(request, "Reviewer unassigned successfully")
        
        return redirect('manage_reviewers', submission_id=submission_id)
    
    return render(request, 'review/manage_reviewers.html', {
        'submission': submission,
        'available_reviewers': available_reviewers,
        'assigned_reviewers': assigned_reviewers,
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    # Check if user is the reviewer
    if review.membership.user != request.user:
        messages.error(request, "You are not authorized to edit this review")
        return redirect('review_list')
    
    # Check if user is still a reviewer and still assigned to this submission
    if review.membership.role1 != Role.REVIEWER or not ReviewerAssignment.objects.filter(
        reviewer=review.membership,
        submission=review.submission
    ).exists():
        messages.error(request, "You are no longer assigned to review this submission")
        return redirect('review_list')
    
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully")
            return redirect('review_list')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'review/edit_review.html', {
        'form': form,
        'review': review,
    })
