from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from main.models import Reservation
from main.utils import logger


@login_required
def cancel_reservation(request, reservation_id):
    """Отменяет бронирование пользователя."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id, user=request.user)
    if reservation.status == "active":
        if reservation.order:
            reservation.order.cancel()
        else:
            reservation.cancel()
        logger.info(f"Пользователь {request.user.username} отменил бронь #{reservation_id}")
    return redirect("active_reservations")
