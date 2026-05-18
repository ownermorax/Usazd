import requests
import json
import re
from pathlib import Path
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta, timezone
from .forms import NeuralNetworkForm
from .classes import YandexAPI


def normalize_text(text):
    return text.lower().replace("ё", "е").strip()


def simplify_station_name(full_name):
    simplified = re.sub(r"\s*\([^)]*\)", "", full_name).strip()
    simplified = re.sub(r"\s+", " ", simplified)
    if not simplified or simplified.lower() == "вокзал":
        return full_name.lower()
    return simplified.lower()


def extract_all_words_from_station(station_title):
    words = []

    match = re.match(r"^(.*?)\s*\(([^)]+)\)$", station_title)
    if match:
        main_part = match.group(1).strip()
        bracket_part = match.group(2).strip()

        main_words = main_part.split()
        bracket_words = bracket_part.split()

        words.extend(main_words)
        words.extend(bracket_words)
    else:
        words = station_title.split()

    words = [normalize_text(w) for w in words if w.lower() not in ["вокзал", "станция"]]

    return words


def calculate_word_similarity(query_word, station_word):
    if not query_word or not station_word:
        return 0.0

    query_word = normalize_text(query_word)
    station_word = normalize_text(station_word)

    if query_word == station_word:
        return 1.0

    if len(query_word) < 2 or len(station_word) < 2:
        return 0.0

    if query_word in station_word:
        if len(query_word) >= len(station_word) * 0.6:
            return 0.9
        else:
            return 0.0

    if station_word in query_word:
        if len(station_word) >= len(query_word) * 0.6:
            return 0.9
        else:
            return 0.0

    m = len(query_word)
    n = len(station_word)

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0

    max_len = get_max_len(dp, m, max_len, n, query_word, station_word)

    if max_len == 0:
        return 0.0

    min_len = min(m, n)
    max_len_word = max(m, n)

    if max_len < min_len * 0.5:
        return 0.0

    if max_len < max_len_word * 0.4:
        return 0.0

    ratio1 = max_len / m
    ratio2 = max_len / n

    avg_ratio = (ratio1 + ratio2) / 2

    return avg_ratio


def get_max_len(dp, m, max_len, n, query_word, station_word):
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if query_word[i - 1] == station_word[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
    return max_len


def calculate_similarity_score(query_word, station_info):
    query_word = normalize_text(query_word)
    station_title = normalize_text(station_info["title"])

    station_words = extract_all_words_from_station(station_info["title"])

    if not station_words:
        return 0.0

    best_score = 0.0

    for sw in station_words:
        if len(sw) < 2:
            continue
        word_score = calculate_word_similarity(query_word, sw)
        if word_score > best_score:
            best_score = word_score

    return best_score


def station_matches_query_word(station_info, query_word):
    query_word = normalize_text(query_word)
    if not query_word or len(query_word) < 2:
        return False

    station_title = normalize_text(station_info["title"])

    if f" {query_word} " in f" {station_title} ":
        return True

    station_words = extract_all_words_from_station(station_info["title"])
    for sw in station_words:
        if sw == query_word:
            return True

    return False


def load_train_stations():
    project_root = Path(settings.BASE_DIR)
    stations_path = project_root / "stations.json"

    if not stations_path.exists():
        print(f"Файл stations.json не найден в {project_root}")
        return {}

    try:
        with open(stations_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            stations = {}
            simplified_stations = {}

            if isinstance(data, dict) and "countries" in data:
                for country in data["countries"]:
                    if "regions" in country:
                        for region in country["regions"]:
                            if "settlements" in region:
                                for settlement in region["settlements"]:
                                    if "stations" in settlement:
                                        for station in settlement["stations"]:
                                            transport_type = station.get("transport_type", "")
                                            if transport_type == "train":
                                                title = station.get("title", "")
                                                yandex_code = station.get("codes", {}).get("yandex_code", "")
                                                if title and yandex_code:
                                                    stations[title.lower()] = {"title": title, "code": yandex_code}

                                                    simplified = simplify_station_name(title)
                                                    if simplified and simplified not in simplified_stations:
                                                        simplified_stations[simplified] = {
                                                            "title": title,
                                                            "code": yandex_code,
                                                        }

            stations.update(simplified_stations)
            return stations
    except Exception as e:
        print(f"Ошибка загрузки станций: {e}")
        return {}


def find_best_matching_stations(query_word, stations_dict, min_score=0.5, max_results=10):
    query_word = normalize_text(query_word)
    if not query_word or len(query_word) < 2:
        return []

    exact_matches = []
    for station_lower, station_info in stations_dict.items():
        if station_matches_query_word(station_info, query_word):
            exact_matches.append((1.0, station_info))

    if exact_matches:
        seen = set()
        unique_matches = []
        for score, station in exact_matches:
            if station["title"].lower() not in seen:
                seen.add(station["title"].lower())
                unique_matches.append((score, station))
        if unique_matches:
            return unique_matches[:max_results]

    scored_matches = []
    for station_lower, station_info in stations_dict.items():
        score = calculate_similarity_score(query_word, station_info)
        if score >= min_score:
            scored_matches.append((score, station_info))

    scored_matches.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    unique_matches = []
    for score, station in scored_matches:
        if station["title"].lower() not in seen:
            seen.add(station["title"].lower())
            unique_matches.append((score, station))

    return unique_matches[:max_results]


def extract_resources_from_query(query, stations_dict):
    query_lower = query.lower()
    query_words = query_lower.split()

    stop_words = get_stop_words()
    query_words = [w for w in query_words if w not in stop_words]

    result = get_init_result()

    if len(query_words) < 1:
        return result

    word_matches = {}

    get_word_matches(query_words, stations_dict, word_matches)

    if len(query_words) == 1:
        word = query_words[0]
        if word in word_matches and len(word_matches[word]) > 0:
            if_second_matches(result, word_matches[word])

    elif len(query_words) >= 2:
        first_matches, second_matches = get_second_atr(query_words, word_matches)

        if first_matches and second_matches:
            get_best_result(first_matches, result, second_matches)

        elif first_matches and not second_matches:
            if_first_matches(first_matches, result)

        elif second_matches and not first_matches:
            if_second_matches(result, second_matches)

        get_last_result(result, word_matches)

    date_patterns = get_date_patterns()

    for pattern in date_patterns:
        match = re.search(pattern, query)
        if match:
            result["date"] = match.group()
            break

    if not result["date"]:
        get_time(result)

    get_another_result(query_lower, result)

    return result


def get_another_result(query_lower, result):
    if any(word in query_lower for word in ["расписание", "когда", "во сколько", "график", "поезд", "электричка"]):
        result["resource_type"] = "schedule"
    elif any(word in query_lower for word in ["свободн", "есть место", "билет", "забронировать", "купить"]):
        result["resource_type"] = "availability"
        result["has_tickets"] = True
    else:
        result["resource_type"] = "schedule"


def get_time(result):
    moscow_tz = timezone(timedelta(hours=3))
    moscow_time = datetime.now(moscow_tz)
    result["date"] = moscow_time.strftime("%Y-%m-%d")


def get_date_patterns():
    date_patterns = [
        r"(\d{2})[./-](\d{2})[./-](\d{4})",
        r"(\d{4})[./-](\d{2})[./-](\d{2})",
    ]
    return date_patterns


def if_second_matches(result, second_matches):
    best = second_matches[0][1]
    result["to_station"] = best["title"].lower()
    result["to_station_code"] = best["code"]
    result["to_station_title"] = best["title"]


def if_first_matches(first_matches, result):
    best = first_matches[0][1]
    result["from_station"] = best["title"].lower()
    result["from_station_code"] = best["code"]
    result["from_station_title"] = best["title"]


def get_best_result(first_matches, result, second_matches):
    best_from, best_to = get_best_form(first_matches, second_matches)
    result["from_station"] = best_from["title"].lower()
    result["from_station_code"] = best_from["code"]
    result["from_station_title"] = best_from["title"]
    result["to_station"] = best_to["title"].lower()
    result["to_station_code"] = best_to["code"]
    result["to_station_title"] = best_to["title"]


def get_last_result(result, word_matches):
    if not result["from_station"] and not result["to_station"]:
        all_matches = []
        for word, matches in word_matches.items():
            for score, station in matches:
                all_matches.append((score, station))

        all_matches.sort(key=lambda x: x[0], reverse=True)

        if len(all_matches) >= 2:
            result["from_station"] = all_matches[0][1]["title"].lower()
            result["from_station_code"] = all_matches[0][1]["code"]
            result["from_station_title"] = all_matches[0][1]["title"]

            for score, station in all_matches[1:]:
                if station["title"].lower() != result["from_station"]:
                    result["to_station"] = station["title"].lower()
                    result["to_station_code"] = station["code"]
                    result["to_station_title"] = station["title"]
                    break
        elif len(all_matches) == 1:
            result["to_station"] = all_matches[0][1]["title"].lower()
            result["to_station_code"] = all_matches[0][1]["code"]
            result["to_station_title"] = all_matches[0][1]["title"]


def get_second_atr(query_words, word_matches):
    first_word = query_words[0]
    second_word = query_words[1]
    first_matches = word_matches.get(first_word, [])
    second_matches = word_matches.get(second_word, [])
    return first_matches, second_matches


def get_best_form(first_matches, second_matches):
    first_stations = [m[1] for m in first_matches]
    second_stations = [m[1] for m in second_matches]
    best_from = first_stations[0]
    best_to = second_stations[0]
    if best_from["title"].lower() == best_to["title"].lower():
        if len(second_stations) > 1:
            best_to = second_stations[1]
        elif len(first_stations) > 1:
            best_from = first_stations[1]
    return best_from, best_to


def get_init_result():
    result = {
        "from_station": None,
        "from_station_code": None,
        "from_station_title": None,
        "to_station": None,
        "to_station_code": None,
        "to_station_title": None,
        "date": None,
        "resource_type": None,
        "has_tickets": False,
    }
    return result


def get_stop_words():
    stop_words = [
        "из",
        "от",
        "со",
        "с",
        "в",
        "до",
        "на",
        "расписание",
        "когда",
        "во",
        "сколько",
        "график",
        "поезд",
        "электричка",
        "свободн",
        "есть",
        "место",
        "билет",
        "забронировать",
        "купить",
    ]
    return stop_words


def get_word_matches(query_words, stations_dict, word_matches):
    for query_word in query_words:
        matching_stations = find_best_matching_stations(query_word, stations_dict, min_score=0.5)
        if matching_stations:
            word_matches[query_word] = matching_stations


def simplify_station_name_for_display(full_name):
    simplified = re.sub(r"\s*\([^)]*\)", "", full_name).strip()
    simplified = re.sub(r"\s+", " ", simplified)
    if not simplified or simplified.lower() == "вокзал":
        return full_name
    return simplified


def format_trains_response(trains_data, from_station_title, to_station_title, date):
    if not trains_data or isinstance(trains_data, str):
        return None

    if "segments" not in trains_data:
        return None

    segments = trains_data.get("segments", [])

    if not segments:
        return f"На {date} поездов из {from_station_title} в {to_station_title} не найдено."

    max_trains = 3
    response_parts = [f"Расписание поездов из {from_station_title} в {to_station_title} на {date}:"]
    response_parts.append("")

    for i, segment in enumerate(segments[:max_trains], 1):
        thread = segment.get("thread", {})
        train_name = thread.get("title", "Поезд")
        number = thread.get("number", "")

        departure = segment.get("departure", "")
        arrival = segment.get("arrival", "")

        dep_time = departure.split("T")[1][:5] if "T" in departure else departure
        arr_time = arrival.split("T")[1][:5] if "T" in arrival else arrival

        duration = segment.get("duration", 0)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        duration_str = f"{hours}ч {minutes}мин" if hours > 0 else f"{minutes}мин"

        from_station_display = simplify_station_name_for_display(
            segment.get("from", {}).get("title", from_station_title)
        )
        to_station_display = simplify_station_name_for_display(segment.get("to", {}).get("title", to_station_title))

        response_parts.append(f"{i}. {train_name} {number}: {from_station_display} -> {to_station_display}")
        response_parts.append(f"   Отправление: {dep_time}, Прибытие: {arr_time}, В пути: {duration_str}")
        response_parts.append("")

    if len(segments) > max_trains:
        response_parts.append(f"* Показаны первые {max_trains} поезда из {len(segments)}")

    return "\n".join(response_parts)


def search_form(request):
    form = NeuralNetworkForm(request.GET or None)
    search_query = None
    search_answer = None
    schedule_link = None
    booking_link = None
    from_station = None
    to_station = None
    trains_data = None

    if form.is_valid():
        booking_link, date, from_code, from_station, schedule_link, search_query, stations_dict, to_code, to_station = (
            get_atr(booking_link, form, from_station, schedule_link, search_query, to_station)
        )

        if from_code and to_code:
            try:
                search_answer, trains_data = get_search_answer(
                    date, from_code, from_station, search_answer, to_code, to_station, trains_data
                )

            except Exception as e:
                print(f"Ошибка получения расписания: {e}")
                import traceback

                traceback.print_exc()
                search_answer = f"Ошибка при получении расписания: {str(e)}"
        else:
            search_answer = if_not_atr_in_question(from_station, search_answer, stations_dict, to_station)

    return {
        "search_form": form,
        "search_query": search_query,
        "search_answer": search_answer,
        "schedule_link": schedule_link,
        "booking_link": booking_link,
        "from_station": from_station,
        "to_station": to_station,
        "trains_data": trains_data,
    }


def get_atr(booking_link, form, from_station, schedule_link, search_query, to_station):
    search_query = form.cleaned_data["text"]
    stations_dict = load_train_stations()
    extracted_info = extract_resources_from_query(search_query, stations_dict)
    from_station = extracted_info["from_station_title"]
    to_station = extracted_info["to_station_title"]
    from_code = extracted_info["from_station_code"]
    to_code = extracted_info["to_station_code"]
    date = extracted_info["date"]
    schedule_link = "/timetable/"
    booking_link = "/timetable/"
    return booking_link, date, from_code, from_station, schedule_link, search_query, stations_dict, to_code, to_station


def if_not_atr_in_question(from_station, search_answer, stations_dict, to_station):
    if not from_station and not to_station:
        search_answer = "Укажите станции отправления и назначения. Например: 'Долгопрудная Москва'"
    elif not from_station:
        search_answer = f"Найдена станция назначения: {to_station}. Укажите станцию отправления."
    elif not to_station:
        search_answer = f"Найдена станция отправления: {from_station}. Укажите станцию назначения."
    else:
        if stations_dict:
            search_answer = f"Не удалось найти коды станций для {from_station} -> {to_station}"
        else:
            search_answer = (
                "Для поиска билетов и расписания укажите конкретные станции. Например: 'билеты от Новодачной до Лобни'"
            )
    return search_answer


def get_search_answer(date, from_code, from_station, search_answer, to_code, to_station, trains_data):
    yandex_api = YandexAPI()
    yandex_api.load_stations_to_memory()
    response = yandex_api.station_request(from_code, to_code, date)
    if isinstance(response, str):
        search_answer = f"Не удалось найти маршрут из {from_station} в {to_station}. Возможно, между этими станциями нет прямого сообщения."
    elif isinstance(response, dict):
        if "segments" in response:
            trains_data = response
            search_answer = format_trains_response(trains_data, from_station, to_station, date)
        elif "error" in response:
            search_answer = f"Ошибка API: {response['error']}"
        else:
            search_answer = (
                f"Не удалось получить расписание из {from_station} в {to_station} на {date}. Попробуйте другую дату."
            )
    else:
        search_answer = f"Сервис временно недоступен. Пожалуйста, попробуйте позже."
    return search_answer, trains_data
