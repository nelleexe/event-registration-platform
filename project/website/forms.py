from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import *


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request = ..., *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Введите Ваш адрес электронной почты'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Введите Ваш пароль'})
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
        labels = {
            'username': _('Электронная почта'),
            'password': _('Пароль')
        }

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['surname'].widget.attrs.update({'placeholder': 'Введите Вашу фамилию'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Введите Ваше имя'})
        self.fields['patronymic'].widget.attrs.update({'placeholder': 'Введите Ваше отчество'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Введите Ваш номер телефона'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Введите Ваш адрес электронной почты'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Введите Ваш пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите Ваш пароль'})
    
    class Meta:
        model = CustomUser
        fields = ('surname', 'name', 'patronymic', 'phone', 'email')
        labels = {
            'surname': _('Фамилия'),
            'name': _('Имя'),
            'patronymic': _('Отчество'),
            'phone': _('Номер телефона'),
            'email': _('Электронная почта')
        }