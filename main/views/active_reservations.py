from main.models import Train as TrainModel, Profile, Reservation, Station
from django.shortcuts import redirect, render


def active_reservations(request):
    """Отображение активных бронирований пользователя"""
    if not request.user.is_authenticated:
        return redirect('auth')

    reservations = Reservation.objects.filter(
        user=request.user,
        status='active'
    ).order_by('-reservation_date')

    return render(request, 'active_reservations.html', {
        'reservations': reservations
    })