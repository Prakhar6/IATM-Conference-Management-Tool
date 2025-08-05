from django.shortcuts import render, get_object_or_404
from .models import Conference
from django.contrib.auth.decorators import login_required

@login_required
def conference_list_view(request):
    conferences = Conference.objects.all()
    return render(request, 'conference/conference_list.html', {'conferences': conferences})

@login_required
def conference_detail_view(request, slug):
    conference = get_object_or_404(Conference, slug=slug)
    return render(request, 'conference/conference_detail.html', {'conference': conference})
