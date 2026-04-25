from django.shortcuts import render


def update_balance(request):
    """
    Отображает страницу пополнения баланса.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    return render(request, 'balance.html')