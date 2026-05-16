from django.shortcuts import render
from main.utils import logger

def custom_404(request, exception):
    """
    Пользовательская страница ошибки 404.

    :param request: HTTP запрос
    :param exception: исключение
    :return: HTTP ответ с шаблоном 404.html и статусом 404
    """
    logger.warning(f"404 ошибка: {request.path}")
    print("aaa")
    return render(request, '404.html', status=404)