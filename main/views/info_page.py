from django.shortcuts import render


def info(request):
    """
    Отображает информационную страницу.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    return render(request, 'info.html')