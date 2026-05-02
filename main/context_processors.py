import requests
import json
from pathlib import Path
from django.conf import settings
from django.urls import reverse
from datetime import datetime
from .forms import NeuralNetworkForm
from .classes import YandexAPI


def load_train_stations():
    """Загружает список железнодорожных станций из файла с кодами"""
    project_root = Path(settings.BASE_DIR)
    stations_path = project_root / 'stations.json'

    if not stations_path.exists():
        print(f"Файл stations.json не найден в {project_root}")
        return {}

    try:
        with open(stations_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            stations = {}  # {название: код}
            # Также создаем словарь с упрощенными названиями
            simplified_stations = {}

            if isinstance(data, dict) and 'countries' in data:
                for country in data['countries']:
                    if 'regions' in country:
                        for region in country['regions']:
                            if 'settlements' in region:
                                for settlement in region['settlements']:
                                    if 'stations' in settlement:
                                        for station in settlement['stations']:
                                            transport_type = station.get('transport_type', '')
                                            if transport_type == 'train':
                                                title = station.get('title', '')
                                                yandex_code = station.get('codes', {}).get('yandex_code', '')
                                                if title and yandex_code:
                                                    stations[title.lower()] = {
                                                        'title': title,
                                                        'code': yandex_code
                                                    }

                                                    # Добавляем упрощенное название (без названия города в скобках)
                                                    simplified = simplify_station_name(title)
                                                    if simplified and simplified not in simplified_stations:
                                                        simplified_stations[simplified] = {
                                                            'title': title,
                                                            'code': yandex_code
                                                        }

            # Объединяем оба словаря (оригинальный поиск имеет приоритет)
            stations.update(simplified_stations)
            return stations
    except Exception as e:
        print(f"Ошибка загрузки станций: {e}")
        return {}


def simplify_station_name(full_name):
    """Упрощает название станции, убирая город в скобках"""
    import re
    # Убираем текст в скобках вместе со скобками
    simplified = re.sub(r'\s*\([^)]*\)', '', full_name).strip()
    # Убираем лишние пробелы
    simplified = re.sub(r'\s+', ' ', simplified)
    # Если после упрощения осталось только слово "Вокзал" или пустая строка, возвращаем оригинал
    if not simplified or simplified.lower() == 'вокзал':
        return full_name.lower()
    return simplified.lower()


def extract_resources_from_query(query, stations_dict):
    """Извлекает из запроса станции, дату и тип запроса"""
    query_lower = query.lower()

    result = {
        'from_station': None,
        'from_station_code': None,
        'from_station_title': None,
        'to_station': None,
        'to_station_code': None,
        'to_station_title': None,
        'date': None,
        'resource_type': None,
        'has_tickets': False
    }

    # Поиск станций
    found_stations = []
    for station_lower, station_info in stations_dict.items():
        if station_lower in query_lower:
            found_stations.append(station_info)

    # Определяем станции
    if len(found_stations) >= 2:
        words = query_lower.split()
        for i, word in enumerate(words):
            if word in ['из', 'от', 'со', 'с'] and i + 1 < len(words):
                for station in found_stations:
                    if station['title'].lower() in words[i + 1] or simplify_station_name(station['title']) in words[
                        i + 1]:
                        result['from_station'] = station['title'].lower()
                        result['from_station_code'] = station['code']
                        result['from_station_title'] = station['title']
                        break
            elif word in ['в', 'до', 'на'] and i + 1 < len(words):
                for station in found_stations:
                    station_simplified = simplify_station_name(station['title'])
                    if (station['title'].lower() in words[i + 1] or station_simplified in words[i + 1]) and station[
                        'title'].lower() != result['from_station']:
                        result['to_station'] = station['title'].lower()
                        result['to_station_code'] = station['code']
                        result['to_station_title'] = station['title']
                        break

        if not result['from_station'] and found_stations:
            result['from_station'] = found_stations[0]['title'].lower()
            result['from_station_code'] = found_stations[0]['code']
            result['from_station_title'] = found_stations[0]['title']
        if not result['to_station'] and len(found_stations) > 1:
            result['to_station'] = found_stations[1]['title'].lower()
            result['to_station_code'] = found_stations[1]['code']
            result['to_station_title'] = found_stations[1]['title']
    elif len(found_stations) == 1:
        result['to_station'] = found_stations[0]['title'].lower()
        result['to_station_code'] = found_stations[0]['code']
        result['to_station_title'] = found_stations[0]['title']

    # Поиск даты
    import re
    date_patterns = [
        r'(\d{2})[./-](\d{2})[./-](\d{4})',
        r'(\d{4})[./-](\d{2})[./-](\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, query)
        if match:
            result['date'] = match.group()
            break

    # Если дата не найдена, используем сегодняшнюю
    if not result['date']:
        result['date'] = datetime.now().strftime('%Y-%m-%d')

    # Тип запроса
    if any(word in query_lower for word in ['расписание', 'когда', 'во сколько', 'график', 'поезд', 'электричка']):
        result['resource_type'] = 'schedule'
    elif any(word in query_lower for word in ['свободн', 'есть место', 'билет', 'забронировать', 'купить']):
        result['resource_type'] = 'availability'
        result['has_tickets'] = True
    else:
        result['resource_type'] = 'schedule'

    return result


def format_trains_response(trains_data, from_station_title, to_station_title, date):
    """Форматирует ответ с конкретными поездами из данных Яндекс.Расписания - показывает только 2-3 поезда"""

    # Проверяем, что данные валидны
    if not trains_data or isinstance(trains_data, str):
        return None

    if 'segments' not in trains_data:
        return None

    segments = trains_data.get('segments', [])

    if not segments:
        return f"На {date} поездов из {from_station_title} в {to_station_title} не найдено."

    # Показываем максимум 3 поезда
    max_trains = 3
    response_parts = [f"Расписание поездов из {from_station_title} в {to_station_title} на {date}:"]
    response_parts.append("")

    for i, segment in enumerate(segments[:max_trains], 1):
        # Получаем информацию о поезде
        thread = segment.get('thread', {})
        train_name = thread.get('title', 'Поезд')
        number = thread.get('number', '')

        # Время отправления и прибытия
        departure = segment.get('departure', '')
        arrival = segment.get('arrival', '')

        dep_time = departure.split('T')[1][:5] if 'T' in departure else departure
        arr_time = arrival.split('T')[1][:5] if 'T' in arrival else arrival

        # Длительность
        duration = segment.get('duration', 0)
        hours = duration // 60
        minutes = duration % 60
        duration_str = f"{hours}ч {minutes}мин" if hours > 0 else f"{minutes}мин"

        # Упрощаем названия станций для отображения
        from_station_display = simplify_station_name_for_display(
            segment.get('from', {}).get('title', from_station_title))
        to_station_display = simplify_station_name_for_display(segment.get('to', {}).get('title', to_station_title))

        response_parts.append(
            f"{i}. {train_name} {number}: {from_station_display} -> {to_station_display}"
        )
        response_parts.append(f"   Отправление: {dep_time}, Прибытие: {arr_time}, В пути: {duration_str}")
        response_parts.append("")

    # Если поездов больше 3, добавляем информацию
    if len(segments) > max_trains:
        response_parts.append(f"* Показаны первые {max_trains} поезда из {len(segments)}")

    return "\n".join(response_parts)


def simplify_station_name_for_display(full_name):
    """Упрощает название станции для отображения пользователю"""
    import re
    # Убираем текст в скобках вместе со скобками
    simplified = re.sub(r'\s*\([^)]*\)', '', full_name).strip()
    # Убираем лишние пробелы
    simplified = re.sub(r'\s+', ' ', simplified)
    # Если после упрощения осталось только слово "Вокзал" или пустая строка, возвращаем оригинал
    if not simplified or simplified.lower() == 'вокзал':
        return full_name
    return simplified


def search_form(request):
    """
    Контекстный процессор с ИИ-помощником для поиска ресурсов и свободных мест
    """
    form = NeuralNetworkForm(request.GET or None)
    search_query = None
    search_answer = None
    schedule_link = None
    booking_link = None
    from_station = None
    to_station = None
    trains_data = None

    if form.is_valid():
        search_query = form.cleaned_data['text']

        # Загружаем станции
        stations_dict = load_train_stations()

        # Извлекаем информацию из запроса
        extracted_info = extract_resources_from_query(search_query, stations_dict)
        from_station = extracted_info['from_station_title']
        to_station = extracted_info['to_station_title']
        from_code = extracted_info['from_station_code']
        to_code = extracted_info['to_station_code']
        date = extracted_info['date']

        # Обе кнопки ведут на timetable
        schedule_link = '/timetable/'
        booking_link = '/timetable/'

        # Если есть коды станций - получаем реальные поезда через YandexAPI
        if from_code and to_code:
            try:
                # Создаем экземпляр API и загружаем станции в память
                yandex_api = YandexAPI()
                yandex_api.load_stations_to_memory()

                # Получаем расписание
                print(f"Запрос к API: {from_code} -> {to_code}, дата: {date}")
                response = yandex_api.station_request(from_code, to_code, date)

                print(f"Ответ API тип: {type(response)}")

                # Проверяем ответ
                if isinstance(response, dict):
                    if 'segments' in response:
                        trains_data = response
                        search_answer = format_trains_response(trains_data, from_station, to_station, date)
                        print(f"Найдено сегментов: {len(response.get('segments', []))}")
                    elif 'error' in response:
                        search_answer = f"Ошибка API: {response['error']}"
                    else:
                        search_answer = f"Не удалось получить расписание из {from_station} в {to_station} на {date}. Попробуйте другую дату."
                else:
                    search_answer = f"Сервис временно недоступен. Пожалуйста, попробуйте позже."

            except Exception as e:
                print(f"Ошибка получения расписания: {e}")
                import traceback
                traceback.print_exc()
                search_answer = f"Ошибка при получении расписания: {str(e)}"
        else:
            # Если станции не найдены - ищем ближайшие совпадения
            if stations_dict:
                suggestions = list(stations_dict.keys())[:10]
                search_answer = f"Не удалось найти станции в вашем запросе. Вот доступные станции: {', '.join(suggestions)}"
            else:
                search_answer = "Для поиска билетов и расписания укажите конкретные станции. Например: 'билеты от Новодачной до Лобни'"

    return {
        'search_form': form,
        'search_query': search_query,
        'search_answer': search_answer,
        'schedule_link': schedule_link,
        'booking_link': booking_link,
        'from_station': from_station,
        'to_station': to_station,
        'trains_data': trains_data,
    }