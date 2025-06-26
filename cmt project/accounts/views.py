from django.shortcuts import render, redirect
from .forms import login_form, register_form
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser


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
        form = register_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('profile')
    else:
        form = register_form()
    
    return render(request, 'accounts/register.html', {'form':form})


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
