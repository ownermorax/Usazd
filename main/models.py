from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """Модель профиля"""
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    def __str__(self):
        return self.user.username

class Users(models.Model):
    """Модель пользователей"""
    username = models.CharField(max_length=80, unique=True)
    user_id = models.AutoField(primary_key=True)
    passwd = models.CharField(max_length=128)
    role = models.CharField(max_length=20, default='user')  # admin, user, manager
    def __str__(self):
        return self.username


class Station(models.Model):
    """Модель станций"""
    station_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name


class Train(models.Model):
    """Модель поездов"""
    train_id = models.AutoField(primary_key=True)
    id_station_start = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_start')
    id_station_stop = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_stop')
    station_at_time = models.DateTimeField()
    path = models.TextField(blank=True)

    def __str__(self):
        return f"Поезд #{self.train_id}"


class Reservation(models.Model):
    """Модель бронирования"""
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='train')
    place_num = models.CharField(max_length=10)
    station_in = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_in')
    station_out = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_out')
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f"Бронь #{self.reservation_id}"