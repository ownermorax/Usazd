from main.models import Profile, Order
from django.shortcuts import redirect, render
from main.utils import logger


def active_reservations(request):
    """Отображение активных бронирований пользователя"""
    logger.info("Пользователь зашел на страницу с активными бронированиями.")
    if not request.user.is_authenticated:
        return redirect("auth")

    orders = Order.objects.filter(user=request.user, status="active").prefetch_related(
        "reservations__train", "reservations__station_in", "reservations__station_out"
    )

    logger.debug(
        f"Найдено заказов: {orders.count()} для пользователя #{request.user.id}."
    )
    return render(request, "active_reservations.html", {"orders": orders})
