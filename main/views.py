from django.shortcuts import render, get_object_or_404, redirect
from main.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import login
from main.forms import RegistrationForm

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "profile.html", context)

def reg(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    return render(request, "registration/reg.html", {'form': form})
def info(request):
    """
    Отображает информационную страницу.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    return render(request, 'info.html')


def index(request):
    """
    Главная страница сайта.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном index.html
    """
    return render(request, 'index.html')


def autho(request):
    """
    Страница авторизации пользователя.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном autho.html
    """
    return render(request, 'autho.html')


def timetable(request):
    """
    Страница с расписанием.

    :param request: HttpRequest
    :returns: HttpResponse с шаблоном timetable.html
    """
    return render(request, 'timetable.html')