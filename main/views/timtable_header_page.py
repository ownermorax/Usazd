from django.http import JsonResponse
from main.api_instance import yandex_api as yandexAPI
import datetime
from main.utils import logger


def timetable_handler(request):
    """
    Обработчик запросов к API для поиска расписания поездов.

    Эндпоинт принимает GET параметры с кодами станций и датой,
    выполняет запрос к Яндекс.Расписанию и возвращает структурированный JSON ответ.

    **GET параметры:**

    :param request: HTTP запрос с параметрами
    :type request: HttpRequest

    **Query parameters:**

    :param str from_code: Код станции отправления (обязательный)
    :param str to_code: Код станции назначения (обязательный)
    :param str date: Дата в формате ГГГГ-ММ-ДД (необязательный, по умолчанию сегодня)
    :param str lang: Язык ответа (необязательный, по умолчанию 'ru_RU')

    :returns: JSON ответ с результатами поиска
    :rtype: JsonResponse

    **Формат ответа:**

    Успешный ответ (status=ok):

    .. code-block:: json

        {
            "status": "ok",
            "data": {
                "search": {...},
                "segments": [...],
                "interval_segments": [...],
                "pagination": {...},
                "from_station": "Симферополь",
                "from_code": "c146",
                "to_station": "Москва",
                "to_code": "c213",
                "date": "2026-03-07",
                "total": 5,
                "trains": [...]
            },
            "error": ""
        }

    Ответ с ошибкой (status=error):

    .. code-block:: json

        {
            "status": "error",
            "message": "Не указаны станции отправления и назначения"
        }

    **Структура объекта поезда (train_info):**

    :param str number: Номер поезда
    :param str title: Название маршрута
    :param str transport_type: Тип транспорта
    :param str departure_station: Станция отправления
    :param str departure_time: Время отправления (ЧЧ:ММ)
    :param str departure_date: Дата отправления
    :param str departure_full: Полная дата и время отправления
    :param str arrival_station: Станция прибытия
    :param str arrival_time: Время прибытия (ЧЧ:ММ)
    :param str arrival_date: Дата прибытия
    :param str arrival_full: Полная дата и время прибытия
    :param int duration_seconds: Длительность в секундах
    :param int duration_hours: Длительность в часах
    :param int duration_minutes: Длительность в минутах
    :param str duration_text: Длительность в формате "Хч Yм"
    :param str carrier: Название перевозчика
    :param str carrier_url: Сайт перевозчика
    :param str carrier_phone: Телефон перевозчика
    :param str stops: Количество остановок
    :param bool has_transfers: Есть ли пересадки
    :param str from_code: Код станции отправления
    :param str to_code: Код станции назначения
    :param str thread_uid: UID нитки расписания
    """
    logger.info("Пользователь запросил расписание.")
    from_name = request.GET.get('from_code', '')
    to_name = request.GET.get('to_code', '')
    
    logger.debug(f"Маршрут: {from_name} -> {to_name}ю")
    
    date = request.GET.get('date', '')
    lang = request.GET.get('lang', 'ru_RU')
    from_code = yandexAPI.get_station_id(from_name)
    to_code = yandexAPI.get_station_id(to_name)
    print(from_name, to_name, from_code, to_code)
    if not from_code or not to_code:
        logger.error("Пользователь не указал станции отправления и назначения.")
        return JsonResponse({
            'status': 'error',
            'message': 'Не указаны станции отправления и назначения'
        }, status=400)
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    result = yandexAPI.station_request(from_code, to_code, date, lang)
    context = {
        'status': 'ok',
        'data': {
            'search': result.get('search', {}),
            'segments': result.get('segments', []),
            'interval_segments': result.get('interval_segments', []),
            'pagination': result.get('pagination', {}),
            'from_station': result.get('search', {}).get('from', {}).get('title', ''),
            'from_code': result.get('search', {}).get('from', {}).get('code', ''),
            'to_station': result.get('search', {}).get('to', {}).get('title', ''),
            'to_code': result.get('search', {}).get('to', {}).get('code', ''),
            'date': result.get('search', {}).get('date', ''),
            'total': result.get('pagination', {}).get('total', 0),
            'trains': []
        },
        'error': ''
    }
    for segment in result.get('segments', []):
        thread = segment.get('thread', {})
        from_info = segment.get('from', {})
        to_info = segment.get('to', {})
        carrier = thread.get('carrier', {})
        duration = segment.get('duration', 0)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        train_info = {
            'number': thread.get('number', ''),
            'title': thread.get('title', ''),
            'transport_type': thread.get('transport_type', ''),
            'departure_station': from_info.get('title', ''),
            'departure_time': segment.get('departure', '')[11:16] if segment.get('departure') else '',
            'departure_date': segment.get('departure', '')[:10] if segment.get('departure') else '',
            'departure_full': segment.get('departure', ''),
            'arrival_station': to_info.get('title', ''),
            'arrival_time': segment.get('arrival', '')[11:16] if segment.get('arrival') else '',
            'arrival_date': segment.get('arrival', '')[:10] if segment.get('arrival') else '',
            'arrival_full': segment.get('arrival', ''),
            'duration_seconds': duration,
            'duration_hours': hours,
            'duration_minutes': minutes,
            'duration_text': f'{hours}ч {minutes}м',
            'carrier': carrier.get('title', ''),
            'carrier_url': carrier.get('url', ''),
            'carrier_phone': carrier.get('phone', ''),
            'stops': segment.get('stops', ''),
            'has_transfers': segment.get('has_transfers', False),
            'from_code': from_info.get('code', ''),
            'to_code': to_info.get('code', ''),
            'thread_uid': thread.get('uid', ''),
            'price': 1000,
        }
        context['data']['trains'].append(train_info)

    return JsonResponse(context)

