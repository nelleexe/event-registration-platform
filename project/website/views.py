from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import *


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
        print(form.errors)
        print(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/profile/')
    else:
        form = CustomUserCreationForm()

    data = {
        'form': form
    }

    return render(request, 'registration/register.html', data)

def login_required(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        else:
            return redirect('/login/')
    return wrapper

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'remove_photo' in request.POST:
            if user.photo:
                user.photo.delete(save=False)
                user.photo = None
                user.save()
                messages.success(request, 'Фото удалено')

        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль сохранён')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    
    else:
        form = ProfileForm(instance=user)
    
    return render(request, "profile.html", {'form': form, 'user_obj': user})

@login_required
def events_view(request):
    data = {
        'events': Event.objects.all(),
        'shedule': Schedule.objects.all()
    }
    return render(request, 'events.html', data)

@login_required
def clubs_view(request):
    data = {
        'clubs': Club.objects.all(),
        'shedule': Schedule.objects.all()

    }
    return render(request, 'clubs.html', data)