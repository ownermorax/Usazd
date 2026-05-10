from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from djmoney.money import Money


class Profile(models.Model):
    """Модель профиля пользователя

    Расширяет стандартную модель User, добавляя личную информацию,
    роль пользователя и баланс.

    :var user: Связь один-к-одному с моделью User
    :var name: Имя пользователя в системе
    :var role: Роль пользователя в системе
    :var description: Описание профиля (необязательное поле)
    :var avatar: Аватар пользователя (необязательно, загружается в 'avatars/'
    :var balance: Денежный баланс"""
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='username')
    role = models.CharField(max_length=20, default='user')
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    balance = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        default=1000
    )

    def __str__(self):
        return self.user.username

    def update_balance(self, money):
        """Обновляет баланс пользователя, сохраняет данные в БД"""
        if isinstance(money, (int, float)):
            money = Money(money, self.balance.currency)
        self.balance += money
        self.save()


class Station(models.Model):
    """Модель станций, хранит название и ID отдельной станции

    :var station_id: ID станции
    :var name: Названия станции"""
    station_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name


class Train(models.Model):
    """Модель поездов, хранит ID отдельного поезда, начальную и конечную станции,
    время отправления и путь следования

    :var train_id: ID поезда
    :var id_station_start: ID начальной станции
    :var id_station_stop: ID конечной станции
    :var station_at_time Время отправления:
    :var path: Путь следования"""
    train_id = models.AutoField(primary_key=True)
    id_station_start = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_start')
    id_station_stop = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_stop')
    station_at_time = models.DateTimeField()
    path = models.TextField(blank=True)

    def __str__(self):
        return f"Поезд #{self.train_id}"


class Reservation(models.Model):
    """Модель бронирования, хранит информацию об ID бронирования, пользователе, поезде,
    статусе бронирования, месте, станций начала и конца маршрута и номер места

    :var reservation_id: ID бронирования
    :var user: Пользователь, совершивший бронирование
    :var train: Поезд с забронированным местом
    :var place_num: Номер забронированного места
    :var station_in: Станция начала муршрута
    :var station_out: Станция конца маршрута
    :var reservation_date: Дата бронирования
    :var status: Статус бронирования"""
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='train')
    place_num = models.CharField(max_length=10)
    station_in = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_in')
    station_out = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_out')
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f"Бронь #{self.reservation_id}"


class Roles(models.Model):
    """Модель ролей, хранит данные о роли пользователя

    :var user: Связь один-к-одному с моделью User
    :var role: Роль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('VIP', 'VIP')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
