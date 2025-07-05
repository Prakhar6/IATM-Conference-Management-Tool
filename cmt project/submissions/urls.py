from django.urls import path
from . import views

urlpatterns = [
    path('create/<slug:slug>/', views.create_submission, name='create_submission'),
    path('<int:pk>/', views.submission_detail, name='submission_detail'),
    path('', views.submission_list, name='submission_list'),
    path('edit/<int:pk>/', views.edit_submission, name='edit_submission'),
    path('delete/<int:pk>/', views.delete_submission, name='delete_submission')
]