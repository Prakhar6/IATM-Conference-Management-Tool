from django.db.models import Q
from membership.models import Membership, Role

def is_reviewer(request):
    user = request.user
    reviewer_status = False
    if user.is_authenticated:
        if user.is_staff:
            reviewer_status = True
        else:
            reviewer_status = Membership.objects.filter(
                user=user
            ).filter(
                Q(role1=Role.REVIEWER) | Q(role2=Role.REVIEWER)
            ).exists()
    return {
        'is_reviewer': reviewer_status
    }

def is_chair(request):
    user = request.user
    chair_status = False
    if user.is_authenticated:
        if user.is_staff:
            chair_status = True
        else:
            chair_status = Membership.objects.filter(
                user=user
            ).filter(
                Q(role1=Role.CHAIR) | Q(role2=Role.CHAIR)
            ).exists()
    return {
        'is_chair': chair_status
    }