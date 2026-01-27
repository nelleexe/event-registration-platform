from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phone_field import PhoneField



# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле электронной почты обязательно')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)  



class CustomUser(AbstractBaseUser, PermissionsMixin):
    surname = models.CharField('Фамилия', max_length=200)
    name = models.CharField('Имя', max_length=200)
    patronymic = models.CharField('Отчество', max_length=200)
    phone = PhoneField('Номер телефона', unique=True)
    email = models.EmailField('Электронная почта', unique=True)
    password = models.CharField('Пароль', max_length=88)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['surname', 'name', 'patronymic', 'phone']

    def str(self):
        return f"{self.surname} {self.name} {self.patronymic}"
    

    class Meta:
            verbose_name = 'пользователя'
            verbose_name_plural = 'Пользователи'