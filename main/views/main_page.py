from django.shortcuts import render


def main(request):
    """
    Главная страница сайта.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном index.html
    """
    return render(request, 'index.html')