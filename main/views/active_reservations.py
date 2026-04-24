from main.models import Train as TrainModel, Profile, Reservation, Station
from django.shortcuts import redirect, render
from main.utils import logger


def active_reservations(request):  # TODO: переделать docstring комментарий
    """Отображение активных бронирований пользователя"""
    logger.info("Пользователь зашел на страницу с активными бронированиями.")
    if not request.user.is_authenticated:
        return redirect('auth')

    reservations = Reservation.objects.filter(
        user=request.user,
        status='active'
    ).order_by('-reservation_date')
    logger.debug(f"Найдено бронирований: {reservations.count()} для пользователя #{request.user.id}.")
    return render(request, 'active_reservations.html', {
        'reservations': reservations
    })
