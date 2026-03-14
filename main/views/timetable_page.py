from django.shortcuts import render


def timetable(request):
    """
    Страница с расписанием.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном timetable.html
    """
    return render(request, 'timetable.html')