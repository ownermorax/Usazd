from django.shortcuts import render
from main.utils import logger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def vip(request, username):
    user = User.objects.get(username=username)
    logger.info("Пользователь зашел на страницу vip.")
    return render(request, "vip.html", {"user": user})
