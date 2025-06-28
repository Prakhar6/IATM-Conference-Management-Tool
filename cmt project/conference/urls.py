from django.urls import path
from . import views
from membership.views import register_for_conference, admin_conference_dashboard_view

urlpatterns = [
    path('', views.conference_list_view, name='conference_list'),
    path('<slug:slug>/', views.conference_detail_view, name = 'conference_detail'),
    path('register/<slug:slug>/', register_for_conference, name='register_for_conference'),
    path('<slug:slug>/admin-dashboard/', admin_conference_dashboard_view, name='admin_conference_dashboard'),

]