import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from djmoney.money import Money

from main.models import Profile, Reservation, Station, Train


@pytest.fixture
def user():
    """Создает тестового пользователя.

    :return: Объект пользователя
    :rtype: User
    """
    return User.objects.create_user(username="testuser", password="123456")


@pytest.fixture
def auth_client(client, user):
    """Создает авторизованный тестовый клиент.

    :param client: Тестовый клиент
    :param user: Тестовый пользователь
    :return: Авторизованный клиент
    :rtype: Client
    """
    client.login(username="testuser", password="123456")
    return client


@pytest.fixture
def profile(user):
    """Создает профиль для тестового пользователя.

    :param user: Тестовый пользователь
    :return: Объект профиля
    :rtype: Profile
    """
    return Profile.objects.create(user=user, balance=Money(100, "USD"))


@pytest.fixture
def stations():
    """Создает тестовые станции.

    :return: Кортеж из двух станций
    :rtype: tuple
    """
    station1 = Station.objects.create(station_id=1, name="Москва")
    station2 = Station.objects.create(station_id=2, name="СПб")
    return station1, station2


@pytest.fixture
def train(stations):
    """Создает тестовый поезд.

    :param stations: Тестовые станции
    :return: Объект поезда
    :rtype: Train
    """
    station1, station2 = stations
    return Train.objects.create(
        id_station_start=station1,
        id_station_stop=station2,
        station_at_time="2026-01-01 10:00:00",
        path=json.dumps({"number": "777"}),
    )


@pytest.fixture
def app_config():
    from main.apps import MainConfig

    return MainConfig.__new__(MainConfig)


@pytest.fixture
def factory():
    return RequestFactory()
