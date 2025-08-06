from django.urls import path
from . import views

urlpatterns = [
    path('chair/assignments/', views.chair_review_assignments, name='chair_review_assignments'),
    path('chair/assign/<int:submission_id>/', views.assign_reviewers_to_submission, name='assign_reviewers_to_submission'),
    path('dashboard/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('submit/<int:review_id>/', views.submit_review, name='submit_review'),
    path('author/reviews/', views.author_reviews, name='author_reviews'),
    path('debug/<int:conference_id>/', views.debug_reviewers, name='debug_reviewers'),
]
