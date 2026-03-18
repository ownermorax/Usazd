from django.shortcuts import render
from main.models import Profile

def user_info(request):
    """
    Страница с личной информацией пользователя.

    Отображает персональные данные текущего авторизованного пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном user_info.html
    :rtype: HttpResponse
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'user_info.html', {'profile':profile})
