from django.shortcuts import render


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