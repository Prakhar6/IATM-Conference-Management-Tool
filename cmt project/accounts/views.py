from django.shortcuts import render, redirect
from .forms import login_form, CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    form = login_form(request.POST or None, request=request)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('profile')

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! You've successfully registered.")
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})




def profile_view(request):
    return render(request, 'accounts/profile.html', {'user':request.user})

def profile_edit_view(request):
    pass

def logout_view(request):
    logout(request)
    return redirect('login')


def home_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('login')
