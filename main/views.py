from django.shortcuts import render, get_object_or_404, redirect
from main.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import login
from main.forms import RegistrationForm
from main.classes import YandexAPI, Train, Carriage,Seat
from django.http import JsonResponse
import datetime

def train(request):#TODO: переделать docstring коментарий
    """Функция для отображения страницы поезда"""

    train = Train()
    carriages_data = []
    for carriage in train.carriages:
        seats_data = []
        for seats in carriage.seats:
            seats_data.append({
                'number': seats.number,
                'is_taken': seats.is_taken,
            })


        carriages_data.append({
            'number': carriage.number,
            'seats': seats_data,
        })

    context = {
            'train': train,
            'carriages': carriages_data,
    }
    return render(request, "train.html", context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "profile.html", context)

def reg(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    return render(request, "registration/reg.html", {'form': form})
def info(request):
    """
    Отображает информационную страницу.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    return render(request, 'info.html')


def index(request):
    """
    Главная страница сайта.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном index.html
    """
    return render(request, 'index.html')


def user_info(request):
    """
    Страница с личной информацией пользователя.

    Отображает персональные данные текущего авторизованного пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном user_info.html
    :rtype: HttpResponse
    """
    return render(request, 'user_info.html')


def active_reservations(request):
    """
    Страница с активными бронями пользователя.

    Отображает список текущих активных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном active_reservations.html
    :rtype: HttpResponse
    """
    return render(request, 'active_reservations.html')


def reservation_history(request):
    """
    Страница с историей броней пользователя.

    Отображает список завершенных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном reservation_history.html
    :rtype: HttpResponse
    """
    return render(request, 'reservation_history.html')

def autho(request):
    """
    Страница авторизации пользователя.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном autho.html
    """
    return render(request, 'autho.html')


def timetable(request):
    """
    Страница с расписанием.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном timetable.html
    """
    return render(request, 'timetable.html')

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

    from_code = request.GET.get('from_code', '')
    to_code = request.GET.get('to_code', '')
    date = request.GET.get('date', '')
    lang = request.GET.get('lang', 'ru_RU')
    if not from_code or not to_code:
        return JsonResponse({
            'status': 'error',
            'message': 'Не указаны станции отправления и назначения'
        }, status=400)
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    yandexAPI = YandexAPI()
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
        }
        context['data']['trains'].append(train_info)

    return JsonResponse(context)

