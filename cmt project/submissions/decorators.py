from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from membership.models import Membership

def require_paid_membership(view_func):
    """
    Decorator to check if user has paid for conference access.
    Must be used after @login_required decorator.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Extract conference slug from kwargs or request
        slug = kwargs.get('slug')
        if not slug:
            # Try to get from request if not in kwargs
            slug = request.GET.get('slug') or request.POST.get('slug')
        
        if not slug:
            messages.error(request, "Conference not specified")
            return redirect('conference_list')
        
        # Check if user has paid membership
        try:
            membership = Membership.objects.get(user=request.user, conference__slug=slug)
            if not membership.is_paid:
                messages.warning(request, "You must complete payment to access this feature")
                return redirect('conference_detail', slug=slug)
        except Membership.DoesNotExist:
            messages.error(request, "You must register for this conference first")
            return redirect('conference_detail', slug=slug)
        
        return view_func(request, *args, **kwargs)
    return wrapper
