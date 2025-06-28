from django.db import models
from accounts.models import CustomUser
from conference.models import Conference

class Role(models.TextChoices):
    AUTHOR = 'Author', 'Author'
    REVIEWER = 'Reviewer', 'Reviewer'
    CHAIR = 'Chair', 'Chair'
    NA = 'N/A', 'N/A'

class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    ACCEPTED = 'Accepted', 'Accepted'
    REJECTED = 'Rejected', 'Rejected'
    WITHDRAWN = 'Withdrawn', 'Withdrawn'

class Membership(models.Model):
    # Represents a user's membership in a conference (Foreign Keys)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='memberships')
    
    
    role1 = models.CharField(max_length=50, choices=Role.choices, default=Role.AUTHOR)
    role2 = models.CharField(max_length=50, choices=Role.choices, default=Role.NA)

    is_paid = models.BooleanField(default=False)

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'conference')

    def __str__(self):
        return f"{self.user.username} - {self.conference.conference_name} ({self.role1}, {self.role2})"