from django.shortcuts import render
from main.utils import logger


def timetable(request):
    """
    Страница с расписанием.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном timetable.html
    """
    logger.info("Пользователь зашел на страницу с расписанием.")
    return render(request, "timetable.html")
