from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('create/<int:submission_id>/', views.create_review, name='create_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('manage/<int:submission_id>/', views.manage_reviewers, name='manage_reviewers'),
] 