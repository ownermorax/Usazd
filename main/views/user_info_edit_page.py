from django.shortcuts import render, redirect

def edit_user_info(request):
    """
    Изменяет личные данные пользователя.

    Обрабатывает POST-запрос и обновляет поля модели Profile: имя, описание, аватар.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: ответ с шаблоном 'user_info_edit.html'
    :rtype: HttpResponse
    """
    profile = request.user.profile
    if request.method == "POST":
        profile.name = request.POST.get("name", profile.name)
        profile.description = request.POST.get("description", profile.description)
        if request.POST.get("delete_avatar"):
            profile.avatar.delete(save=False)
            profile.avatar = None
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        profile.save()

        return redirect("profile", request.user.username)
    return render(request, "user_info_edit.html", {"profile": profile})