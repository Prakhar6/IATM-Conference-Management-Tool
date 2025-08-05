from django.db import models
from django.conf import settings
from submissions.models import Submissions

class Review(models.Model):
    submission = models.ForeignKey(Submissions, on_delete=models.CASCADE, related_name='reviews', null=True)
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

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission.paper_title}"
