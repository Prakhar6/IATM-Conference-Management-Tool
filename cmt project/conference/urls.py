from django.urls import path
from . import views

urlpatterns = [
    path('', views.conference_list_view, name='conference_list'),
    path('/<slug:slug>/', views.conference_detail, name = 'conference_detail')

]