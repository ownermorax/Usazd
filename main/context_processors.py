from .forms import NeuralNetworkForm
from .classes import YandexAPI
from .context_processor_helper import *


def search_form(request):
    """Обрабатывает поисковую форму и возвращает контекст для шаблона."""
    form = NeuralNetworkForm(request.GET or None)
    search_query = None
    search_answer = None
    schedule_link = None
    booking_link = None
    from_station = None
    to_station = None
    trains_data = None

    if form.is_valid():
        (
            booking_link,
            date,
            from_code,
            from_station,
            schedule_link,
            search_query,
            stations_dict,
            to_code,
            to_station,
        ) = get_atr(
            booking_link, form, from_station, schedule_link, search_query, to_station
        )

        if from_code and to_code:
            try:
                search_answer, trains_data = get_search_answer(
                    date,
                    from_code,
                    from_station,
                    search_answer,
                    to_code,
                    to_station,
                    trains_data,
                )

            except Exception as e:
                search_answer = f"Ошибка при получении расписания: {str(e)}"
        else:
            search_answer = if_not_atr_in_question(
                from_station, search_answer, stations_dict, to_station
            )

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
    """Извлекает атрибуты из формы поиска."""
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
    return (
        booking_link,
        date,
        from_code,
        from_station,
        schedule_link,
        search_query,
        stations_dict,
        to_code,
        to_station,
    )


def if_not_atr_in_question(from_station, search_answer, stations_dict, to_station):
    """Формирует ответ, если станции не найдены в запросе."""
    if not from_station and not to_station:
        search_answer = (
            "Укажите станции отправления и назначения. Например: 'Долгопрудная Москва'"
        )
    elif not from_station:
        search_answer = (
            f"Найдена станция назначения: {to_station}. Укажите станцию отправления."
        )
    elif not to_station:
        search_answer = (
            f"Найдена станция отправления: {from_station}. Укажите станцию назначения."
        )
    else:
        if stations_dict:
            search_answer = (
                f"Не удалось найти коды станций для {from_station} -> {to_station}"
            )
        else:
            search_answer = "Для поиска билетов и расписания укажите конкретные станции. Например: 'билеты от Новодачной до Лобни'"
    return search_answer
