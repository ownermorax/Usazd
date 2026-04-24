from django.shortcuts import render, redirect
from main.utils import logger


def edit_user_info(request):
    """
    Изменяет личные данные пользователя.

    Обрабатывает POST-запрос и обновляет поля модели Profile: имя, описание, аватар.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: ответ с шаблоном 'user_info_edit.html'
    :rtype: HttpResponse
    """
    logger.info("Пользователь зашел на страницу изменения личной информации.")
    profile = request.user.profile
    if request.method == "POST":
        logger.info(f"Обновление профиля пользователя #{request.user.id}.")
        profile.name = request.POST.get("name", profile.name)
        profile.description = request.POST.get("description", profile.description)
        if request.POST.get("delete_avatar"):
            logger.debug("Пользователь удалил аватар.")
            profile.avatar.delete(save=False)
            profile.avatar = None
        if "avatar" in request.FILES:
            logger.debug("Пользователь загрузил новый аватар.")
            profile.avatar = request.FILES["avatar"]

        profile.save()
        logger.info("Профиль обновлен.")
        return redirect("profile", request.user.username)
    return render(request, "user_info_edit.html", {"profile": profile})
