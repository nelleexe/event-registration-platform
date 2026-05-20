from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, logout, password_validation
from django.contrib import messages
from .models import *
from django.http import HttpResponseForbidden
from datetime import datetime as dt


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
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме входа')
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
            messages.success(request, 'Вы успешно зарегистрировались и вошли в аккаунт')
            return redirect('/profile/')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации')
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
            messages.error(request, 'Пожалуйста, войдите в аккаунт, чтобы получить доступ к этой странице')
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
                messages.error(request, 'Новый пароль слишком простой или распространённый')
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
def unsubscribe_view(request, id):
    user = request.user
    event = BaseEvent.objects.filter(id=id).first()
    if not event:
        messages.error(request, 'Такого мероприятия не существует')
    elif event.id in map(lambda x: x.event.id, EventMember.objects.filter(user=user)):
        subscribe = EventMember.objects.get(user=user, event=event)
        subscribe.delete()
        messages.success(request, f'Вы успешно отменили запись на {subscribe.event.name}')
    else:
        messages.error(request, 'Вы не являетесь участником данного мероприятия')
    try:
        return redirect(request.GET.get('next'))
    except TypeError:
        return redirect('/profile/')

@login_required
def events_view(request):
    data = {
        'events': Event.objects.all(),
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
                    messages.error(request, 'К сожалению, в момент отправки запроса, свободных мест на мероприятие уже не осталось')
            else:
                messages.error(request, 'Вы уже являетесь участником данного мероприятия')
        except:
            messages.error(request, 'Не удалось записаться на мероприятие')
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
                    messages.error(request, 'К сожалению, в момент отправки запроса, в кружке уже было максимальное число участников')
            else:
                messages.error(request, 'Вы уже являетесь участником данного кружка')
        except:
            messages.error(request, 'Не удалось записаться в кружок')
    return render(request, 'clubs.html', data)

@login_required
@login_required

def create_view(request):
    user = request.user

    if user.role != 'organizer':
        messages.error(request, 'Вы не являетесь организатором')
        return redirect('/profile/')

    form = EventCreationForm()
    club_form = ClubCreationForm()
    active_form = 'event'

    if request.method == 'POST':
        active_form = request.POST.get('creation_type', 'event')

        if active_form == 'club':
            club_form = ClubCreationForm(request.POST, request.FILES)

            if club_form.is_valid():
                club = club_form.save(commit=False)
                club.organizer = request.user
                club.save()

                messages.success(request, 'Кружок успешно добавлен')
                return redirect('/create/')
            else:
                messages.error(request, 'Неверные данные кружка')

        else:
            form = EventCreationForm(request.POST, request.FILES)

            if form.is_valid():
                event = form.save(commit=False)
                event.organizer = request.user
                event.save()

                messages.success(request, 'Мероприятие успешно добавлено')
                return redirect('/create/')
            else:
                messages.error(request, 'Неверные данные мероприятия')

    data = {
        'form': form,
        'club_form': club_form,
        'active_form': active_form,
    }

    return render(request, 'create.html', data)
    



'''
Для организаторов сделать отдельную страницу с добавлением мероприятия или кружка (без доступа напрямую в админ-панель);
Форму сделать для добавления мероприятий
Добавить связь родителя и ребёнка через систему заявок;
Сделать систему оповещений;
Чаты по мероприятиям.
Проверка роли при регистрации
Добавить невозможность поставить прошедшее число в создание мероприятия
Другую главную страницу для авторизованного пользователя с полезным функционалом (например календарик на несколько дней)
Добавить календарь событий
'''