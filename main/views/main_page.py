from django.shortcuts import render
from main.utils import logger


def main(request):
    """
    Главная страница сайта.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном index.html
    """
    logger.info("Пользователь зашел на главную страницу.")
    return render(request, 'main.html')
