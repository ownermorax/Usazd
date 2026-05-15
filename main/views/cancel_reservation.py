from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from main.models import Reservation
from main.utils import logger

@login_required
def cancel_reservation(request, reservation_id):
    """
    Отмена активного бронирования.

    Изменяет статус бронирования на 'cancelled'.

    :param request: HTTP запрос
    :param reservation_id: ID бронирования
    :return: перенаправление на страницу активных броней
    """
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if reservation.status == 'active':
        reservation.status = 'cancelled'
        reservation.save()
        logger.info(f"Пользователь {request.user.username} отменил бронь #{reservation_id}")
    return redirect('active_reservations')