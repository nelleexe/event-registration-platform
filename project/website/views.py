from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, logout


# Create your views here.
def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = CustomAuthenticationForm()
    
    data = {
        'form': form
    }

    return render(request, 'registration/login.html', data)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/') #profile
    else:
        form = CustomUserCreationForm()

    data = {
        'form': form
    }

    return render(request, 'registration/register.html', data)