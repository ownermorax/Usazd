from django.test import RequestFactory
import json
from unittest.mock import patch, MagicMock, PropertyMock
import pytest
from django.contrib.auth.models import User
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
    assert "orders" in response.context


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


@pytest.mark.django_db
def test_user_info_page(auth_client):
    response = auth_client.get(reverse("user_info"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_info_profile_created(auth_client, user):
    auth_client.get(reverse("user_info"))
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_edit_user_info_get(auth_client, profile):
    response = auth_client.get(reverse("edit_user_info"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_user_info_post(auth_client, profile):
    response = auth_client.post(reverse("edit_user_info"), {"name": "NewName"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_edit_user_info_name_changed(auth_client, profile):
    auth_client.post(reverse("edit_user_info"), {"name": "Changed"})
    profile.refresh_from_db()
    assert profile.name == "Changed"


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


@pytest.mark.django_db
def test_reservation_missing_data(client):
    response = client.get(reverse("create_reservation"))
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_user_not_found(client):
    response = client.get(
        reverse("create_reservation"),
        {"username": 999, "train_id": "777", "seats": "1x1"},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_no_station(client, profile):
    response = client.get(
        reverse("create_reservation"),
        {"username": profile.user.id, "train_id": "777", "seats": "1x1"},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_success(client, profile, stations):
    station1, station2 = stations

    response = client.get(
        reverse("create_reservation"),
        {
            "username": profile.user.id,
            "train_id": "777",
            "seats": "1x1",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_reservation_created(client, profile, stations):
    station1, station2 = stations

    client.get(
        reverse("create_reservation"),
        {
            "username": profile.user.id,
            "train_id": "777",
            "seats": "1x1",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

    assert Reservation.objects.exists()


@pytest.mark.django_db
def test_reservation_balance_decreased(client, profile, stations):
    station1, station2 = stations
    old_balance = profile.balance

    client.get(
        reverse("create_reservation"),
        {
            "username": profile.user.id,
            "train_id": "777",
            "seats": "1x1",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

    profile.refresh_from_db()
    assert profile.balance < old_balance


@pytest.mark.django_db
def test_reservation_not_enough_money(client, user, stations):
    profile = Profile.objects.create(user=user, balance=Money(0, "USD"))
    station1, station2 = stations

    response = client.get(
        reverse("create_reservation"),
        {
            "username": user.id,
            "train_id": "777",
            "seats": "1x1",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

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
        status="active",
    )

    response = client.get(
        reverse("create_reservation"),
        {
            "username": profile.user.id,
            "train_id": "777",
            "seats": "1x1",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_reservation_multiple_seats(client, profile, stations):
    station1, station2 = stations

    response = client.get(
        reverse("create_reservation"),
        {
            "username": profile.user.id,
            "train_id": "777",
            "seats": "1x1W1x2W1x3",
            "station_in": station1.station_id,
            "station_out": station2.station_id,
        },
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_timetable_missing_params(client):
    response = client.get(reverse("timetable_api"))
    assert response.status_code == 400


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_invalid_station(mock_station, client):
    mock_station.return_value = None

    response = client.get(reverse("timetable_api"), {"from_code": "A", "to_code": "B"})

    assert response.status_code == 400


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_success(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {"search": {}, "segments": [], "pagination": {}}

    response = client.get(
        reverse("timetable"), {"from_code": "Москва", "to_code": "СПб"}
    )

    assert response.status_code == 200


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_json(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {"search": {}, "segments": [], "pagination": {}}

    response = client.get(
        reverse("timetable_api"), {"from_code": "Москва", "to_code": "СПб"}
    )

    assert response.json()["status"] == "ok"


@pytest.mark.django_db
@patch("main.api_instance.yandex_api.station_request")
@patch("main.api_instance.yandex_api.get_station_id")
def test_timetable_contains_data(mock_station, mock_request, client):
    mock_station.return_value = "c123"
    mock_request.return_value = {"search": {}, "segments": [], "pagination": {}}

    response = client.get(
        reverse("timetable_api"), {"from_code": "Москва", "to_code": "СПб"}
    )

    assert "data" in response.json()


@pytest.mark.django_db
def test_create_station():
    station = Station.objects.create(station_id=1, name="Казань")
    assert station.name == "Казань"


@pytest.mark.django_db
def test_create_train(stations):
    station1, station2 = stations
    train = Train.objects.create(
        id_station_start=station1,
        id_station_stop=station2,
        station_at_time="2026-01-01 10:00:00",
        path="{}",
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
        status="active",
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
def test_reservation_history_page(auth_client):
    response = auth_client.get(reverse("reservation_history"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_timetable_page(client):
    response = client.get(reverse("timetable"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_balance_page(auth_client):
    response = auth_client.get(reverse("balance"))
    assert response.status_code == 200


def test_app_name(app_config):
    assert app_config.name == "main"


def test_default_auto_field(app_config):
    assert app_config.default_auto_field == "django.db.models.BigAutoField"


def test_normalize_text_lowercase():
    from main.context_processors import normalize_text

    assert normalize_text("Москва") == "москва"


def test_normalize_text_yo():
    from main.context_processors import normalize_text

    assert normalize_text("Ёлка") == "елка"


def test_normalize_text_strip():
    from main.context_processors import normalize_text

    assert normalize_text("  текст  ") == "текст"


def test_simplify_station_name_removes_brackets():
    from main.context_processors import simplify_station_name

    assert simplify_station_name("Москва (Казанская)") == "москва"


def test_simplify_station_name_plain():
    from main.context_processors import simplify_station_name

    assert simplify_station_name("Лобня") == "лобня"


def test_simplify_station_name_only_vokzal():
    from main.context_processors import simplify_station_name

    result = simplify_station_name("Вокзал")
    assert result == "вокзал"


def test_extract_all_words_with_brackets():
    from main.context_processors import extract_all_words_from_station

    words = extract_all_words_from_station("Москва (Казанская)")
    assert "москва" in words
    assert "казанская" in words


def test_extract_all_words_no_brackets():
    from main.context_processors import extract_all_words_from_station

    words = extract_all_words_from_station("Долгопрудная")
    assert "долгопрудная" in words


def test_extract_all_words_filters_vokzal():
    from main.context_processors import extract_all_words_from_station

    words = extract_all_words_from_station("Вокзал")
    assert "вокзал" not in words


def test_similarity_exact_match():
    from main.context_processors import calculate_word_similarity

    assert calculate_word_similarity("москва", "москва") == 1.0


def test_similarity_empty_string():
    from main.context_processors import calculate_word_similarity

    assert calculate_word_similarity("", "москва") == 0.0


def test_similarity_short_string():
    from main.context_processors import calculate_word_similarity

    assert calculate_word_similarity("а", "москва") == 0.0


def test_similarity_substring():
    from main.context_processors import calculate_word_similarity

    score = calculate_word_similarity("моск", "москва")
    assert score > 0.0


def test_similarity_no_match():
    from main.context_processors import calculate_word_similarity

    score = calculate_word_similarity("zzz", "москва")
    assert score == 0.0


def test_station_matches_exact():
    from main.context_processors import station_matches_query_word

    station = {"title": "Лобня", "code": "s1"}
    assert station_matches_query_word(station, "лобня") is True


def test_station_not_matches():
    from main.context_processors import station_matches_query_word

    station = {"title": "Лобня", "code": "s1"}
    assert station_matches_query_word(station, "москва") is False


def test_station_matches_short_word():
    from main.context_processors import station_matches_query_word

    station = {"title": "Лобня", "code": "s1"}
    assert station_matches_query_word(station, "а") is False


def test_get_stop_words_returns_list():
    from main.context_processors import get_stop_words

    words = get_stop_words()
    assert isinstance(words, list)
    assert "в" in words
    assert "из" in words


def test_get_init_result_keys():
    from main.context_processors import get_init_result

    result = get_init_result()
    assert result["from_station"] is None
    assert result["to_station"] is None
    assert result["has_tickets"] is False


def test_format_trains_response_no_data():
    from main.context_processors import format_trains_response

    assert format_trains_response(None, "А", "Б", "2024-01-01") is None


def test_format_trains_response_no_segments_key():
    from main.context_processors import format_trains_response

    assert format_trains_response({}, "А", "Б", "2024-01-01") is None


def test_format_trains_response_empty_segments():
    from main.context_processors import format_trains_response

    result = format_trains_response({"segments": []}, "А", "Б", "2024-01-01")
    assert "не найдено" in result


def test_format_trains_response_with_data():
    from main.context_processors import format_trains_response

    segment = {
        "thread": {"title": "Экспресс", "number": "001"},
        "departure": "2024-01-01T10:00:00",
        "arrival": "2024-01-01T12:00:00",
        "duration": 7200,
        "from": {"title": "Станция А"},
        "to": {"title": "Станция Б"},
    }
    result = format_trains_response({"segments": [segment]}, "А", "Б", "2024-01-01")
    assert "Экспресс" in result
    assert "10:00" in result


def test_if_not_atr_no_stations():
    from main.context_processors import if_not_atr_in_question

    result = if_not_atr_in_question(None, None, {}, None)
    assert "Укажите станции" in result


def test_if_not_atr_no_from():
    from main.context_processors import if_not_atr_in_question

    result = if_not_atr_in_question(None, None, {}, "Лобня")
    assert "отправления" in result


def test_if_not_atr_no_to():
    from main.context_processors import if_not_atr_in_question

    result = if_not_atr_in_question("Москва", None, {}, None)
    assert "назначения" in result


def test_get_another_result_schedule():
    from main.context_processors import get_another_result

    result = {"resource_type": None, "has_tickets": False}
    get_another_result("расписание электричек", result)
    assert result["resource_type"] == "schedule"


def test_get_another_result_availability():
    from main.context_processors import get_another_result

    result = {"resource_type": None, "has_tickets": False}
    get_another_result("купить билет", result)
    assert result["resource_type"] == "availability"
    assert result["has_tickets"] is True


def test_get_time_sets_date():
    from main.context_processors import get_time

    result = {"date": None}
    get_time(result)
    assert result["date"] is not None
    assert len(result["date"]) == 10  # YYYY-MM-DD


def test_find_best_matching_stations_empty_query():
    from main.context_processors import find_best_matching_stations

    result = find_best_matching_stations(
        "", {"лобня": {"title": "Лобня", "code": "s1"}}
    )
    assert result == []


def test_find_best_matching_stations_exact():
    from main.context_processors import find_best_matching_stations

    stations = {"лобня": {"title": "Лобня", "code": "s1"}}
    result = find_best_matching_stations("лобня", stations)
    assert len(result) > 0
    assert result[0][1]["code"] == "s1"


@patch("main.views.reg_page.RegistrationForm")
def test_get_returns_empty_form(mock_form_class, factory):
    mock_form_class.return_value = MagicMock()
    request = factory.get("/reg/")
    from main.views.reg_page import reg

    response = reg(request)
    assert response.status_code == 200


@patch("main.views.reg_page.login")
@patch("main.views.reg_page.RegistrationForm")
def test_post_valid_form_redirects(mock_form_class, mock_login, factory):
    mock_form = MagicMock()
    mock_form.is_valid.return_value = True
    mock_form.save.return_value = MagicMock(username="testuser")
    mock_form_class.return_value = mock_form

    request = factory.post("/reg/", {"username": "testuser", "password": "123"})
    from main.views.reg_page import reg

    response = reg(request)

    assert response.status_code == 302
    assert response.url == "/"


@patch("main.views.reg_page.RegistrationForm")
def test_post_invalid_form_returns_200(mock_form_class, factory):
    mock_form = MagicMock()
    mock_form.is_valid.return_value = False
    mock_form_class.return_value = mock_form

    request = factory.post("/reg/", {})
    from main.views.reg_page import reg

    response = reg(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_active_reservation_gets_cancelled(client, user, profile, train, stations):
    station1, station2 = stations
    reservation = Reservation.objects.create(
        user=user,
        train=train,
        place_num="1-1",
        station_in=station1,
        station_out=station2,
        status="active",
    )

    client.force_login(user)
    client.post(reverse("cancel_reservation", args=[reservation.pk]))

    reservation.refresh_from_db()
    assert reservation.status == "cancelled"


@pytest.mark.django_db
@patch("main.views.cancel_reservation.get_object_or_404")
def test_non_active_reservation_not_changed(mock_get, factory, user):
    mock_reservation = MagicMock()
    mock_reservation.status = "cancelled"
    mock_get.return_value = mock_reservation

    request = factory.post("/cancel/1/")
    request.user = user

    from main.views.cancel_reservation import cancel_reservation

    cancel_reservation(request, reservation_id=1)

    assert mock_reservation.status == "cancelled"
    mock_reservation.save.assert_not_called()


@pytest.mark.django_db
@patch("main.views.cancel_reservation.get_object_or_404")
def test_redirects_after_cancel(mock_get, factory, user):
    mock_reservation = MagicMock()
    mock_reservation.status = "active"
    mock_get.return_value = mock_reservation

    request = factory.post("/cancel/1/")
    request.user = user

    from main.views.cancel_reservation import cancel_reservation

    response = cancel_reservation(request, reservation_id=1)

    assert response.status_code == 302
