from django.db import models
from django.conf import settings
from accounts.models import CustomUser
from conference.models import Conference

class Role(models.TextChoices):
    AUTHOR = 'Author', 'Author'
    REVIEWER = 'Reviewer', 'Reviewer'
    CHAIR = 'Chair', 'Chair'
    NA = 'N/A', 'N/A'

class Membership(models.Model):
    # Represents a user's membership in a conference (Foreign Keys)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='memberships')

    role1 = models.CharField(max_length=50, choices=Role.choices, default=Role.AUTHOR)
    role2 = models.CharField(max_length=50, choices=Role.choices, default=Role.NA)

    is_paid = models.BooleanField(default=False)
    messaging_opt_in = models.BooleanField(default=True, help_text="Allow other attendees to send you messages")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'conference')

    def __str__(self):
        return f"{self.user.email} - {self.conference.conference_name} ({self.role1}, {self.role2})"


class AttendeeMessage(models.Model):
    """Internal messaging between conference attendees (opt-in only)."""
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.email} -> {self.recipient.email}: {self.subject}"
