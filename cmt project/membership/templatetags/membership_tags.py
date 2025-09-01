from django import template
from membership.models import Membership

register = template.Library()

@register.filter
def has_conference_access(user, conference):
    """Check if user has paid access to a specific conference"""
    try:
        membership = Membership.objects.get(user=user, conference=conference)
        return membership.is_paid
    except Membership.DoesNotExist:
        return False

@register.filter
def get_conference_membership(user, conference):
    """Get user's membership for a specific conference"""
    try:
        return Membership.objects.get(user=user, conference=conference)
    except Membership.DoesNotExist:
        return None
