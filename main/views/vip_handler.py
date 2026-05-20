from django.http import JsonResponse

from main.vip import Vip


def vip_handler(request):
    """Обработчик запроса на добавление VIP статуса.

    Принимает параметры длительности и ID пользователя, добавляет VIP статус.

    :param request: HTTP запрос
    :return: JSON ответ со статусом ok
    :rtype: JsonResponse
    """
    duration_str = request.GET.get("duration")
    user_id = request.GET.get("userid")
    vip = Vip()
    durations = {"1min": 1 / 1440, "1month": 30, "6months": 180, "1year": 365}
    prices = {"1min": 1, "1month": 5, "6months": 25, "1year": 50}
    duration = durations.get(duration_str)
    price = prices.get(duration_str)
    vip.add_vip_user(user_id, duration, price)
    return JsonResponse({"status": "ok"})
