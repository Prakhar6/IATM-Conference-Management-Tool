from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/schedule/', views.conference_schedule, name='conference_schedule'),
    path('<slug:slug>/speakers/', views.speaker_directory, name='speaker_directory'),
    path('session/<int:session_id>/join/', views.join_session, name='join_session'),
]
