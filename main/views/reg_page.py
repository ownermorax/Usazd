from django.contrib.auth import login
from django.shortcuts import redirect, render
from main.forms import RegistrationForm


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
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    return render(request, "registration/reg.html", {'form': form})