from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect_view, name='home_redirect'),
    path('login/', views.login_view, name = 'login'),
    path('register/', views.register_view, name = 'register'),
    path('profile/', views.profile_view, name = 'profile'),
    path('profile/edit', views.profile_edit_view, name = 'profile_edit'),
    path('logout/', views.logout_view, name = 'logout')

]