from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, logout, password_validation
from django.contrib import messages
from .models import *
from django.http import HttpResponseForbidden


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
def password_change_view(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if not user.check_password(old_password):
            messages.error(request, 'Неверный старый пароль')
        elif new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
        elif len(new_password) < 8:
            messages.error(request, 'Новый пароль должен быть не менее 8 символов')
        else:
            try:
                password_validation.validate_password(new_password, user=user)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Пароль успешно изменён')
                return redirect('/login/')
            except:
                messages.error(request, 'Новый пароль слишком простой или распостранённый')
    return render(request, 'registration/password_change.html')

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
        'events': [event for event in Event.objects.all() if event.id not in [club.id for club in Club.objects.all()]],
        'shedule': Schedule.objects.all()
    }
    if request.method == 'POST':
        user = request.user
        event_id = request.POST.get('event-id')
        try:
            event = Event.objects.get(id=event_id)
            members = [enrollment.user for enrollment in EventMember.objects.filter(event=event)]
            if user not in members:
                if len(members) < event.capacity:
                    EventMember(user=user, event=event).save()
                    messages.success(request, f'Вы успешно записались на мероприятие «{event.name}»')
                    return redirect('/profile/')
                else:
                    return HttpResponseForbidden('К сожалению, в момент отправки запроса, свободных мест на меропрятие уже не осталось')
            else:
                return HttpResponseForbidden('Вы уже являетесь участником данного мероприятия')
        except:
            return HttpResponseForbidden('Не удалось записаться на мероприятие')
    return render(request, 'events.html', data)

@login_required
def clubs_view(request):
    data = {
        'clubs': Club.objects.all(),
        'shedule': Schedule.objects.all()
    }
    if request.method == 'POST':
        user = request.user
        club_id = request.POST.get('club-id')
        try:
            club = Club.objects.get(id=club_id)
            members = [enrollment.user for enrollment in EventMember.objects.filter(event=club)]
            if user not in members:
                if len(members) < club.capacity:
                    EventMember(user=user, event=club).save()
                    messages.success(request, f'Вы успешно записались в кружок «{club.name}»')
                    return redirect('/profile/')
                else:
                    return HttpResponseForbidden('К сожалению, в момент отправки запроса, в кружке уже было максимальное число участников')
            else:
                return HttpResponseForbidden('Вы уже являетесь участником данного кружка')
        except:
            return HttpResponseForbidden('Не удалось записаться в кружок')
    return render(request, 'clubs.html', data)


