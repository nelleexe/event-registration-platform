from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
    phone = models.CharField('Номер телефона', unique=True)
    email = models.EmailField('Электронная почта', unique=True)
    photo = models.ImageField('Фотография', upload_to="users/", blank=True, null=True)

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

class WeekDay(models.Model):
    name = models.CharField('Название', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'день недели'
        verbose_name_plural = 'Дни недели'

class Event(models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    capacity = models.IntegerField('Максимальное кол-во участников')
    logo = models.ImageField('Превью', upload_to='events/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'События'

class Schedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Событие')
    weekday = models.ForeignKey(WeekDay, on_delete=models.PROTECT, verbose_name='День недели')
    start_time = models.TimeField('Время начала')
    finish_time = models.TimeField('Время конца')
    place = models.CharField('Место проведения')

    def __str__(self):
        return f'{self.event}:\t{self.weekday} с {self.start_time} до {self.finish_time}'

    class Meta:
        verbose_name = 'расписание'
        verbose_name_plural = 'Расписания'

class Club(Event):
    supervisor = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='Руководитель')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'кружок'
        verbose_name_plural = 'Кружки'

class EventMember(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Событие')
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='Участник')

    def __str__(self):
        return f'{self.user} на {self.event}'
    
    class Meta:
        verbose_name = 'участника'
        verbose_name_plural = 'Участники'


models_list = [CustomUser, WeekDay, Event, Schedule, Club, EventMember]