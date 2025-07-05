from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SubmissionForm
from .models import Submissions
from conference.models import Conference
from membership.models import Membership
from django.contrib import messages
import os
# Create your views here.
@login_required
def create_submission(request, slug):
    conference = get_object_or_404(Conference, slug=slug)
    
    if not Membership.objects.filter(user=request.user, conference=conference).exists():
        messages.error(request, "You are not a member of this conference to submit a paper")
        return redirect('conference_detail', slug=slug)
    
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            membership = Membership.objects.get(user=request.user, conference=conference)
            submission.membership = membership
            submission.save()
            form.save_m2m()
            messages.success(request, "Submission Successfully Submitted")
            return redirect('submission_detail', pk=submission.pk)
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = SubmissionForm()
    return render(request, 'submissions/create_submissions.html', {
        'conference': conference,
        'form': form
    })
@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submissions, pk=pk)
    if submission.membership.user != request.user and not submission.co_authors.filter(id=request.user.id).exists():
        messages.error(request, "You are not authorized to view this submission")
        return redirect('conference_detail', slug=submission.membership.conference.slug)
    return render(request, 'submissions/submission_detail.html', {
        'submission': submission,
        'conference': submission.membership.conference
    })

@login_required
def submission_list(request):
    author_submissions = Submissions.objects.filter(membership__user=request.user)
    coauthor_submissions = Submissions.objects.filter(co_authors=request.user)

    all_submissions = (author_submissions | coauthor_submissions).distinct().order_by('-submission_date')
    return render(request, 'submissions/submission_list.html', {
        'author_submissions': author_submissions,
        'coauthor_submissions': coauthor_submissions,
        'all_submissions': all_submissions,
    })

@login_required
def edit_submission(request, pk):
    submission = get_object_or_404(Submissions, pk=pk)
    
    # Check if user is either main author or co-author
    if submission.membership.user != request.user and not submission.co_authors.filter(id=request.user.id).exists():
        messages.error(request, "You are not authorized to edit this submission")
        return redirect('submission_detail', pk=pk)
    
    # Check if submission is still editable
    if submission.status in ['ACCEPTED', 'REJECTED']:
        messages.error(request, "Cannot edit submission after it has been accepted or rejected")
        return redirect('submission_detail', pk=pk)
    
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission successfully updated")
            return redirect('submission_detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = SubmissionForm(instance=submission)
    
    return render(request, 'submissions/edit_submission.html', {
        'form': form,
        'submission': submission,
        'conference': submission.membership.conference
    })

@login_required
def delete_submission(request, pk):
    submission = get_object_or_404(Submissions, pk=pk)
    
   
    if submission.membership.user != request.user and not submission.co_authors.filter(id=request.user.id).exists():
        messages.error(request, "You are not authorized to delete this submission")
        return redirect('submission_detail', pk=pk)
    
   
    if submission.status == 'ACCEPTED':
        messages.error(request, "Cannot delete an accepted submission")
        return redirect('submission_detail', pk=pk)
    
    if request.method == 'POST':
      
        conference_slug = submission.membership.conference.slug
        
        
        if submission.file:
            if os.path.isfile(submission.file.path):
                os.remove(submission.file.path)
        
        
        submission.delete()
        messages.success(request, "Submission successfully deleted")
        return redirect('conference_detail', slug=conference_slug)
    
    return render(request, 'submissions/delete_confirmation.html', {
        'submission': submission,
        'conference': submission.membership.conference
    })


