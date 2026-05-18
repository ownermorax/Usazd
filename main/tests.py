from django.test import TestCase
import json
from unittest.mock import patch
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from djmoney.money import Money
from main.models import Profile, Reservation, Station, Train


# ========== Фикстуры ==========


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        password="123456"
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username="testuser", password="123456")
    return client


@pytest.fixture
def profile(user):
    return Profile.objects.create(
        user=user,
        balance=Money(100, "USD")
    )


@pytest.fixture
def stations():
    station1 = Station.objects.create(
        station_id=1,
        name="Москва"
    )
    station2 = Station.objects.create(
        station_id=2,
        name="СПб"
    )
    return station1, station2


@pytest.fixture
def train(stations):
    station1, station2 = stations
    return Train.objects.create(
        id_station_start=station1,
        id_station_stop=station2,
        station_at_time="2026-01-01 10:00:00",
        path=json.dumps({"number": "777"})
    )


# ========== Test active reservation page ==========


@pytest.mark.django_db
def test_active_reservations_redirect(client):
    response = client.get(reverse("active_reservations"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_active_reservations_ok(auth_client):
    response = auth_client.get(reverse("active_reservations"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_active_reservations_template(auth_client):
    response = auth_client.get(reverse("active_reservations"))
    assert "active_reservations.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_active_reservations_context(auth_client):
    response = auth_client.get(reverse("active_reservations"))
    assert "reservations" in response.context


# ========== Test profile page ==========


@pytest.mark.django_db
def test_profile_page_exists(client, user):
    response = client.get(reverse("profile", args=[user.username]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_auto_create(client, user):
    client.get(reverse("profile", args=[user.username]))
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_profile_404(client):
    response = client.get(reverse("profile", args=["unknown_user"]))
    assert response.status_code == 404


# ========== Test user info page ==========


@pytest.mark.django_db
def test_user_info_page(auth_client):
    response = auth_client.get(reverse("user_info"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_info_profile_created(auth_client, user):
    auth_client.get(reverse("user_info"))
    assert Profile.objects.filter(user=user).exists()


# ========== Test edit user info page ==========


@pytest.mark.django_db
def test_edit_user_info_get(auth_client, profile):
    response = auth_client.get(reverse("edit_user_info"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_user_info_post(auth_client, profile):
    response = auth_client.post(reverse("edit_user_info"), {
        "name": "NewName"
    })
    assert response.status_code == 302


@pytest.mark.django_db
def test_edit_user_info_name_changed(auth_client, profile):
    auth_client.post(reverse("edit_user_info"), {"name": "Changed"})
    profile.refresh_from_db()
    assert profile.name == "Changed"


# ========== Test train page ==========


@pytest.mark.django_db
def test_train_page(client):
    response = client.get(reverse("train"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_train_page_with_id(client):
    response = client.get(reverse("train"), {"id": "777"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_train_context(client):
    response = client.get(reverse("train"))
    assert "carriages" in response.context


# ========== Test reservation handle ==========


@pytest.mark.django_db
def test_reservation_missing_data(client):
    response = client.get(reverse("create_reservation"))
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_user_not_found(client):
    response = client.get(reverse("create_reservation"), {
        "username": 999,
        "train_id": "777",
        "seats": "1x1"
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_no_station(client, profile):
    response = client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1"
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_success(client, profile, stations):
    station1, station2 = stations

    response = client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    assert response.status_code == 200


@pytest.mark.django_db
def test_reservation_created(client, profile, stations):
    station1, station2 = stations

    client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    assert Reservation.objects.exists()


@pytest.mark.django_db
def test_reservation_balance_decreased(client, profile, stations):
    station1, station2 = stations
    old_balance = profile.balance

    client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    profile.refresh_from_db()
    assert profile.balance < old_balance


@pytest.mark.django_db
def test_reservation_not_enough_money(client, user, stations):
    profile = Profile.objects.create(
        user=user,
        balance=Money(0, "USD")
    )
    station1, station2 = stations

    response = client.get(reverse("create_reservation"), {
        "username": user.id,
        "train_id": "777",
        "seats": "1x1",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_duplicate_seat(client, profile, stations, train):
    station1, station2 = stations

    Reservation.objects.create(
        user=profile.user,
        train=train,
        place_num="1-1",
        station_in=station1,
        station_out=station2,
        status="active"
    )

    response = client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_multiple_seats(client, profile, stations):
    station1, station2 = stations

    response = client.get(reverse("create_reservation"), {
        "username": profile.user.id,
        "train_id": "777",
        "seats": "1x1W1x2W1x3",
        "station_in": station1.station_id,
        "station_out": station2.station_id
    })

    assert response.status_code == 200


# ========== Test timetable ==========


@pytest.mark.django_db
def test_timetable_missing_params(client):
    response = client.get(reverse("timetable_api"))
    assert response.status_code == 400


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_invalid_station(mock_station, client):
    mock_station.return_value = None

    response = client.get(reverse("timetable_api"), {
        "from_code": "A",
        "to_code": "B"
    })

    assert response.status_code == 400


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_success(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {
        "search": {},
        "segments": [],
        "pagination": {}
    }

    response = client.get(reverse("timetable"), {
        "from_code": "Москва",
        "to_code": "СПб"
    })

    assert response.status_code == 200


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_json(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {
        "search": {},
        "segments": [],
        "pagination": {}
    }

    response = client.get(reverse("timetable_api"), {
        "from_code": "Москва",
        "to_code": "СПб"
    })

    assert response.json()["status"] == "ok"


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_contains_data(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {
        "search": {},
        "segments": [],
        "pagination": {}
    }

    response = client.get(reverse("timetable_api"), {
        "from_code": "Москва",
        "to_code": "СПб"
    })

    assert "data" in response.json()


# ========== Extra model tests ==========


@pytest.mark.django_db
def test_create_station():
    station = Station.objects.create(
        station_id=1,
        name="Казань"
    )
    assert station.name == "Казань"


@pytest.mark.django_db
def test_create_train(stations):
    station1, station2 = stations
    train = Train.objects.create(
        id_station_start=station1,
        id_station_stop=station2,
        station_at_time="2026-01-01 10:00:00",
        path='{}'
    )
    assert train is not None


@pytest.mark.django_db
def test_create_reservation(user, stations, train):
    station1, station2 = stations
    reservation = Reservation.objects.create(
        user=user,
        train=train,
        place_num="1-1",
        station_in=station1,
        station_out=station2,
        status="active"
    )
    assert reservation.status == "active"


@pytest.mark.django_db
def test_main_page(client):
    response = client.get(reverse("main"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_info_page(client):
    response = client.get(reverse("info"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_timetable_page(client):
    response = client.get(reverse("timetable"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_balance_page(auth_client):
    response = auth_client.get(reverse("balance"))
    assert response.status_code == 200