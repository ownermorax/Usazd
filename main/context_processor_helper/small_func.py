def simplify_station_name(full_name):
    """Упрощает название станции, удаляя скобки и лишние пробелы."""
    import re

    simplified = re.sub(r"\s*\([^)]*\)", "", full_name).strip()
    simplified = re.sub(r"\s+", " ", simplified)
    if not simplified or simplified.lower() == "вокзал":
        return full_name.lower()
    return simplified.lower()


def normalize_text(text):
    """Приводит текст к нижнему регистру и заменяет ё на е."""
    return text.lower().replace("ё", "е").strip()


def get_max_len(dp, m, max_len, n, query_word, station_word):
    """Вычисляет максимальную длину общей подстроки."""
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if query_word[i - 1] == station_word[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
    return max_len


def get_another_result(query_lower, result):
    """Определяет тип ресурса по ключевым словам в запросе."""
    if any(
        word in query_lower
        for word in [
            "расписание",
            "когда",
            "во сколько",
            "график",
            "поезд",
            "электричка",
        ]
    ):
        result["resource_type"] = "schedule"
    elif any(word in query_lower for word in ["свободн", "есть место", "билет", "забронировать", "купить"]):
        result["resource_type"] = "availability"
        result["has_tickets"] = True
    else:
        result["resource_type"] = "schedule"


def get_time(result):
    """Устанавливает текущую дату в московском часовом поясе."""
    from datetime import datetime, timedelta, timezone

    moscow_tz = timezone(timedelta(hours=3))
    moscow_time = datetime.now(moscow_tz)
    result["date"] = moscow_time.strftime("%Y-%m-%d")


def get_date_patterns():
    """Возвращает регулярные выражения для поиска дат."""
    date_patterns = [
        r"(\d{2})[./-](\d{2})[./-](\d{4})",
        r"(\d{4})[./-](\d{2})[./-](\d{2})",
    ]
    return date_patterns


def if_second_matches(result, second_matches):
    """Заполняет станцию назначения из совпадений."""
    best = second_matches[0][1]
    result["to_station"] = best["title"].lower()
    result["to_station_code"] = best["code"]
    result["to_station_title"] = best["title"]


def if_first_matches(first_matches, result):
    """Заполняет станцию отправления из совпадений."""
    best = first_matches[0][1]
    result["from_station"] = best["title"].lower()
    result["from_station_code"] = best["code"]
    result["from_station_title"] = best["title"]


def get_best_result(first_matches, result, second_matches):
    """Заполняет обе станции из лучших совпадений."""
    best_from, best_to = get_best_form(first_matches, second_matches)
    result["from_station"] = best_from["title"].lower()
    result["from_station_code"] = best_from["code"]
    result["from_station_title"] = best_from["title"]
    result["to_station"] = best_to["title"].lower()
    result["to_station_code"] = best_to["code"]
    result["to_station_title"] = best_to["title"]


def get_second_atr(query_words, word_matches):
    """Получает совпадения для первых двух слов запроса."""
    first_word = query_words[0]
    second_word = query_words[1]
    first_matches = word_matches.get(first_word, [])
    second_matches = word_matches.get(second_word, [])
    return first_matches, second_matches


def get_best_form(first_matches, second_matches):
    """Находит лучшие станции отправления и назначения."""
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
    """Возвращает инициализированный словарь результата."""
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
    """Возвращает список стоп-слов для фильтрации запросов."""
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
    """Находит совпадения станций для каждого слова запроса."""
    from .find_best_matching_stations import find_best_matching_stations

    for query_word in query_words:
        matching_stations = find_best_matching_stations(query_word, stations_dict, min_score=0.5)
        if matching_stations:
            word_matches[query_word] = matching_stations


def simplify_station_name_for_display(full_name):
    """Упрощает название станции для отображения."""
    import re

    simplified = re.sub(r"\s*\([^)]*\)", "", full_name).strip()
    simplified = re.sub(r"\s+", " ", simplified)
    if not simplified or simplified.lower() == "вокзал":
        return full_name
    return simplified
