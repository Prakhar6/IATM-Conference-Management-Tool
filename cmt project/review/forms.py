from django import forms
from .models import Review
from membership.models import Membership, Role
from submissions.models import Submissions

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'recommendation']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
        }

class AssignReviewersForm(forms.Form):
    reviewers = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Select Reviewers",
        help_text="Select multiple reviewers to assign to this submission"
    )

    def __init__(self, *args, **kwargs):
        conference = kwargs.pop('conference', None)
        submission = kwargs.pop('submission', None)
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        if conference:
            # Get all reviewers for this conference - check both role1 and role2
            from django.db.models import Q
            reviewer_memberships = Membership.objects.filter(
                conference=conference
            ).filter(
                Q(role1='Reviewer') | Q(role2='Reviewer')
            ).select_related('user')
            
            # Exclude the submission author and current user (chair) from reviewer options
            excluded_users = set()
            if submission:
                # Exclude the main author
                excluded_users.add(submission.membership.user.id)
                # Exclude co-authors if they exist
                if submission.co_author1:
                    excluded_users.add(submission.co_author1.id)
                if submission.co_author2:
                    excluded_users.add(submission.co_author2.id)
                if submission.co_author3:
                    excluded_users.add(submission.co_author3.id)
            
            if current_user:
                excluded_users.add(current_user.id)
            
            # Filter out excluded users
            if excluded_users:
                reviewer_memberships = reviewer_memberships.exclude(user__id__in=excluded_users)
            
            # Set the queryset and ensure it's properly configured
            self.fields['reviewers'].queryset = reviewer_memberships
            self.fields['reviewers'].label_from_instance = lambda obj: f"{obj.user.get_full_name()} ({obj.user.email})"
