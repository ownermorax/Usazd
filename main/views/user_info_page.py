from django.shortcuts import render

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