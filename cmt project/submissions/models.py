from django.db import models
from membership.models import Membership
from accounts.models import CustomUser
from conference.models import Track

class Submissions(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        REVISION = 'REVISION', 'Needs Revision'

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='submissions')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='submissions')
    paper_title = models.CharField(max_length=255)
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    co_author1 = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='submission_coauthor1'
    )
    co_author2 = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='submission_coauthor2'
    )
    co_author3 = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='submission_coauthor3'
    )

    class Meta:
        unique_together = ('membership', 'paper_title')
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.paper_title} - {self.membership.user.email} ({self.submission_date.date()})"

    def update_status_from_reviews(self):
        """Update submission status based on all submitted reviews"""
        from review.models import Review
        
        # Get all submitted reviews for this submission
        submitted_reviews = Review.objects.filter(
            submission=self,
            is_submitted=True
        ).exclude(recommendation__isnull=True)

        if not submitted_reviews.exists():
            self.status = self.StatusChoices.PENDING
            self.save()
            return

        total_reviews = submitted_reviews.count()
        
        # Check if any review recommends rejection (rejection overrides everything)
        if submitted_reviews.filter(recommendation='REJECT').exists():
            self.status = self.StatusChoices.REJECTED
        # Check if any review recommends revision (revision overrides acceptance)
        elif submitted_reviews.filter(recommendation='REVISE').exists():
            self.status = self.StatusChoices.REVISION
        # Check if all reviews recommend acceptance (need at least 1 review)
        elif total_reviews >= 1 and submitted_reviews.filter(recommendation='ACCEPT').count() == total_reviews:
            self.status = self.StatusChoices.ACCEPTED
        # If there are mixed recommendations or only one review, keep as pending
        else:
            self.status = self.StatusChoices.PENDING

        self.save()
