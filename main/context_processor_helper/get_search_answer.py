def get_search_answer(date, from_code, from_station, search_answer, to_code, to_station, trains_data):
    """Получает ответ на поисковый запрос о расписании поездов."""
    from main.classes import YandexAPI

    from .format_trains_response import format_trains_response

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
