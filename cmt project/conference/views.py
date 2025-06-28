from django.shortcuts import render
from .models import Conference
from django.contrib import messages


def conference_list_view(request):
    conferences = Conference.objects.all()
    return render(request, 'conference/conference_list.html', {'conferences': conferences})

def conference_detail_view(request, slug):
    try:
        conference = Conference.objects.get(slug=slug)
    except Conference.DoesNotExist:
        return render(request, '#', {'slug': slug})

    return render(request, 'conference/conference_detail.html', {'conference': conference})