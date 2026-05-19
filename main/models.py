from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from djmoney.money import Money
import datetime
from decimal import Decimal


class Profile(models.Model):
    """Модель профиля"""

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default="username")
    role = models.CharField(max_length=20, default="user")
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_vip = models.BooleanField(default=False)
    vip_data = models.TextField(blank=True)

    balance = MoneyField(
        max_digits=10, decimal_places=2, default_currency="USD", default=1000
    )

    def __str__(self):
        return self.user.username

    def update_balance(self, money):
        if isinstance(money, (int, float, Decimal)):
            money = Money(money, self.balance.currency)
        self.balance += money
        self.save()

    @property
    def vip_expire(self):
        if self.vip_data:
            return datetime.datetime.fromisoformat(self.vip_data)
        return None


class Station(models.Model):
    """Модель станций"""

    station_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    """Модель поездов"""

    train_id = models.AutoField(primary_key=True)
    id_station_start = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="station_start"
    )
    id_station_stop = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="station_stop"
    )
    station_at_time = models.DateTimeField()
    path = models.TextField(blank=True)

    def __str__(self):
        return f"Поезд #{self.train_id}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="active")

    def cancel(self):
        if self.status != "cancelled":
            self.status = "cancelled"
            self.save()
            reservations = self.reservations.filter(status="active")
            total = Money(2 * reservations.count(), "USD")
            self.user.profile.update_balance(total)
            reservations.update(status="cancelled")


class Reservation(models.Model):
    """Модель бронирования"""

    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="train")
    place_num = models.CharField(max_length=10)
    station_in = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="station_in"
    )
    station_out = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="station_out"
    )
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="active")
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True,
        blank=True,
    )

    def cancel(self):
        if self.status != "cancelled":
            self.status = "cancelled"
            self.save()
            profile = self.user.profile
            profile.update_balance(Money(2, "USD"))

    def __str__(self):
        return f"Бронь #{self.reservation_id}"


class Roles(models.Model):
    """Модель ролей"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (("admin", "Admin"), ("user", "User"), ("VIP", "VIP"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
