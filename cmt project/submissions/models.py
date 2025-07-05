from django.db import models
from membership.models import Membership
from accounts.models import CustomUser
from membership.models import Status
#include track id


# Create your models here.
class Submissions(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='submissions')
    #add track id
    co_authors = models.ManyToManyField(CustomUser, related_name='co_authored_submissions')
    paper_title = models.CharField(max_length=255)
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/')
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
#abstract??
    class Meta:
        unique_together = ('membership', 'paper_title')
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.paper_title} - {self.membership.user.email} ({self.submission_date.date()})"
    