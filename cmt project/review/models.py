from django.db import models
from membership.models import Membership
from submissions.models import Submissions
from django.utils import timezone


# Create your models here.
class Review(models.Model):
    
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='review')
    submission = models.ForeignKey(Submissions, on_delete=models.CASCADE, related_name='review')
    comment = models.TextField()
    date_reviewed = models.DateTimeField(auto_now_add=True)
    RECOMMENDATION_CHOICES = [
        ('ACCEPT', 'Accept'),
        ('REJECT', 'Reject'),
        ('REVISE', 'Needs Revision'),
        ('PENDING', 'Pending'),
    ]
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES, default='PENDING')
    class Meta:
        unique_together = ('membership', 'submission')

    def __str__(self):
        return f"Review by {self.membership.user.username} for {self.submission.paper_title}"
