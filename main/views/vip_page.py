from django.shortcuts import render
from main.utils import logger


def vip(request):
    logger.info("Пользователь зашел на страницу vip.")
    return render(request, 'vip.html')
