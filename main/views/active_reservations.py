from main.models import Train as TrainModel, Profile, Reservation, Station
from django.shortcuts import redirect, render


def active_reservations(request):
    """Отображение активных бронирований пользователя

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном active_reservations.html
    :rtype: HttpResponse"""
    if not request.user.is_authenticated:
        return redirect('auth')

    reservations = Reservation.objects.filter(
        user=request.user,
        status='active'
    ).order_by('-reservation_date')

    return render(request, 'active_reservations.html', {
        'reservations': reservations
    })