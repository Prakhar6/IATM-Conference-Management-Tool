from django.db import models
from django.conf import settings
from submissions.models import Submissions
from django.utils import timezone

class Review(models.Model):
    submission = models.ForeignKey(Submissions, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_assigned')
    comment = models.TextField(blank=True, null=True)
    recommendation_choices = [
        ('ACCEPT', 'Accept'),
        ('REJECT', 'Reject'),
        ('REVISE', 'Needs Revision'),
    ]
    recommendation = models.CharField(max_length=10, choices=recommendation_choices, blank=True, null=True)
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_reviewed = models.DateTimeField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('submission', 'reviewer')
        ordering = ['-date_reviewed', '-date_assigned']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission.paper_title}"

    def save(self, *args, **kwargs):
        # Check if this is a new review or if the recommendation has changed
        if self.pk:
            # This is an existing review, check if recommendation changed
            old_review = Review.objects.get(pk=self.pk)
            recommendation_changed = old_review.recommendation != self.recommendation
            is_submitted_changed = old_review.is_submitted != self.is_submitted
        else:
            # This is a new review
            recommendation_changed = False
            is_submitted_changed = False
        
        # If this is a new review being submitted, set the date
        if self.is_submitted and not self.date_reviewed:
            self.date_reviewed = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update submission status if review was submitted or recommendation changed
        if self.is_submitted and (recommendation_changed or is_submitted_changed or not self.pk):
            self.submission.update_status_from_reviews()



    @classmethod
    def update_all_submission_statuses(cls):
        """Update status for all submissions based on their reviews"""
        from submissions.models import Submissions
        
        for submission in Submissions.objects.all():
            submission.update_status_from_reviews()
