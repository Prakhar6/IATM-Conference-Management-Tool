from django.db import models
from membership.models import Membership
from accounts.models import CustomUser
from conference.models import Track

class Submissions(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'

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
