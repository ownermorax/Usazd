from django.contrib.auth import login
from django.shortcuts import redirect, render
from main.forms import RegistrationForm
from main.utils import logger


def reg(request):
    """
    Регистрирует нового пользователя в системе.

    После регистрации пользователь автоматически авторизируется
    и перенаправляется на гланую стараницу.

    :param request: HTTP-запрос
    :type request: HttpRequest
    :return: HTTP ответ с шаблоном reg.html
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.warning(
                f"Пользователь {user.username} успешно смог зарегистрироваться и войти в аккаунт."
            )
            return redirect("/")
        else:
            logger.warning("Пользователь не смог зарегистрироваться.")

    else:
        form = RegistrationForm()

    return render(request, "registration/reg.html", {"form": form})
