import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from djmoney.money import Money

from main.models import Profile, Reservation, Station, Train
from .tests_helper import *


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

    result = find_best_matching_stations("", {"лобня": {"title": "Лобня", "code": "s1"}})
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


def test_load_train_stations_file_not_exists():
    with patch("pathlib.Path.exists", return_value=False):
        from main.context_processors import load_train_stations

        result = load_train_stations()
        assert result == {}


def test_load_train_stations_returns_stations():
    data = {
        "countries": [
            {
                "regions": [
                    {
                        "settlements": [
                            {
                                "stations": [
                                    {"transport_type": "train", "title": "Москва", "codes": {"yandex_code": "s123"}}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", mock_open(read_data=json.dumps(data))):
        from main.context_processors import load_train_stations

        result = load_train_stations()
        assert "москва" in result
        assert result["москва"]["code"] == "s123"


def test_load_train_stations_skips_non_train():
    data = {
        "countries": [
            {
                "regions": [
                    {
                        "settlements": [
                            {
                                "stations": [
                                    {"transport_type": "bus", "title": "Автовокзал", "codes": {"yandex_code": "s999"}}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", mock_open(read_data=json.dumps(data))):
        from main.context_processors import load_train_stations

        result = load_train_stations()
        assert result == {}


def test_load_train_stations_invalid_json():
    with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", mock_open(read_data="not json")):
        from main.context_processors import load_train_stations

        result = load_train_stations()
        assert result == {}
