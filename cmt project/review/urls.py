from django.urls import path
from . import views

urlpatterns = [
    path('chair/assign/', views.chair_review_assignments, name='chair_review_assignments'),
    path('reviewer/dashboard/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('review/<int:review_id>/submit/', views.submit_review, name='submit_review'),
    path('author/reviews/', views.author_reviews, name='author_reviews'),
]
